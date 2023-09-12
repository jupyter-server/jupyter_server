"""Support for renaming kernel specs at runtime."""
# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.
from functools import wraps
from typing import Any, Dict, Tuple

from jupyter_client.kernelspec import KernelSpecManager
from jupyter_core.utils import ensure_async, run_sync
from traitlets import Unicode, default, observe
from traitlets.config import LoggingConfigurable


def normalize_kernel_name(method):
    @wraps(method)
    async def wrapped_method(self, *args, **kwargs):
        kernel_name = kwargs.get("kernel_name", None)
        if (
            kernel_name
            and hasattr(self, "kernel_spec_manager")
            and hasattr(self.kernel_spec_manager, "original_kernel_name")
        ):
            original_kernel_name = self.kernel_spec_manager.original_kernel_name(kernel_name)
            if kernel_name != original_kernel_name:
                self.log.debug(
                    f"Renamed kernel '{kernel_name}' replaced with original kernel name '{original_kernel_name}'"
                )
                kwargs["renamed_kernel"] = kernel_name
                kwargs["kernel_name"] = original_kernel_name

        return await method(self, *args, **kwargs)

    return wrapped_method


class RenamingKernelSpecManagerMixin(LoggingConfigurable):
    """KernelSpecManager mixin that renames kernel specs.

    The base KernelSpecManager class only has synchronous methods, but some child
    classes (in particular, GatewayKernelManager) change those methods to be async.

    In order to support both versions, we provide both synchronous and async versions
    of all the relevant kernel spec manager methods. We first do the renaming in the
    async version, but override the KernelSpecManager base methods using the
    synchronous versions.
    """

    spec_name_prefix = Unicode(help="Prefix to be added onto the front of kernel spec names.")

    display_name_suffix = Unicode(
        config=True, help="Suffix to be added onto the end of kernel spec display names."
    )

    display_name_format = Unicode(
        config=True, help="Format for rewritten kernel spec display names."
    )

    @default("display_name_format")
    def _default_display_name_format(self):
        if self.display_name_suffix:
            return "{}" + self.display_name_suffix
        return "{}"

    default_kernel_name = Unicode(allow_none=True)

    @observe("default_kernel_name")
    def _observe_default_kernel_name(self, change):
        kernel_name = change.new
        if self.original_kernel_name(kernel_name) is not kernel_name:
            # The default kernel name has already been renamed
            return
        updated_kernel_name = self.rename_kernel(kernel_name)
        self.log.debug(f"Renaming default kernel name {kernel_name} to {updated_kernel_name}")
        self.default_kernel_name = updated_kernel_name

    def rename_kernel(self, kernel_name: str) -> str:
        """Rename the supplied kernel spec based on the configured format string."""
        if kernel_name.startswith(self.spec_name_prefix):
            return kernel_name
        return self.spec_name_prefix + kernel_name

    def original_kernel_name(self, kernel_name: str) -> str:
        if not kernel_name.startswith(self.spec_name_prefix):
            return kernel_name
        return kernel_name[len(self.spec_name_prefix) :]

    def _update_display_name(self, display_name: str) -> str:
        if not display_name:
            return display_name
        return self.display_name_format.format(display_name)

    def _update_spec(self, original_name: str, kernel_spec: Dict) -> Tuple[str, Dict]:
        original_prefix = f"/kernelspecs/{original_name}"
        spec_name = self.rename_kernel(original_name)
        new_prefix = f"/kernelspecs/{spec_name}"

        kernel_spec["name"] = spec_name
        kernel_spec["spec"] = kernel_spec.get("spec", {})
        kernel_spec["resources"] = kernel_spec.get("resources", {})

        spec = kernel_spec["spec"]
        spec["display_name"] = self._update_display_name(spec.get("display_name", ""))

        resources = kernel_spec["resources"]
        for name, value in resources.items():
            resources[name] = value.replace(original_prefix, new_prefix)
        return spec_name, kernel_spec

    async def async_get_all_specs(self):
        ks: Dict = {}
        original_ks = await ensure_async(super().get_all_specs())  # type:ignore[misc]
        for s, k in original_ks.items():
            spec_name, kernel_spec = self._update_spec(s, k)
            ks[spec_name] = kernel_spec
        return ks

    def get_all_specs(self):
        return run_sync(self.async_get_all_specs)()

    async def async_get_kernel_spec(self, kernel_name: str, *args: Any, **kwargs: Any) -> Any:
        original_kernel_name = self.original_kernel_name(kernel_name)
        self.log.debug(f"Found original kernel name '{original_kernel_name}' for '{kernel_name}'")
        kspec = await ensure_async(
            super().get_kernel_spec(original_kernel_name, *args, **kwargs)  # type:ignore[misc]
        )
        if original_kernel_name == kernel_name:
            # The kernel wasn't renamed, so don't modify its contents
            return kspec

        # KernelSpecManager and GatewayKernelSpec manager return different types for the
        # wrapped `get_kernel_spec` call (KernelSpec vs. Dict). To accommodate both,
        # we check the type of the returned value and operate on the two different
        # types as appropriate.
        if isinstance(kspec, dict):
            kspec["name"] = kernel_name
            kspec["display_name"] = self._update_display_name(kspec.get("display_name", ""))
        else:
            kspec.name = kernel_name
            kspec.display_name = self._update_display_name(kspec.display_name)
        return kspec

    def get_kernel_spec(self, kernel_name: str, *args: Any, **kwargs: Any) -> Any:
        return run_sync(self.async_get_kernel_spec)(kernel_name, *args, **kwargs)

    async def get_kernel_spec_resource(self, kernel_name: str, *args: Any, **kwargs: Any) -> Any:
        if not hasattr(super(), "get_kernel_spec_resource"):
            return None
        kernel_name = self.original_kernel_name(kernel_name)
        return await ensure_async(
            super().get_kernel_spec_resource(kernel_name, *args, **kwargs)  # type:ignore[misc]
        )


class RenamingKernelSpecManager(RenamingKernelSpecManagerMixin, KernelSpecManager):
    """KernelSpecManager that renames kernels"""

    spec_name_prefix = Unicode(
        "local-", help="Prefix to be added onto the front of kernel spec names."
    )

    display_name_suffix = Unicode(
        " (Local)",
        config=True,
        help="Suffix to be added onto the end of kernel spec display names.",
    )
