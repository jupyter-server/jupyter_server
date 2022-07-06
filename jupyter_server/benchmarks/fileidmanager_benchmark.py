import os
import timeit

from jupyter_core.paths import jupyter_data_dir

from jupyter_server.services.contents.fileidmanager import FileIdManager

db_path = os.path.join(jupyter_data_dir(), "file_id_manager_perftest.db")


def build_setup(n, insert=True):
    def setup():
        try:
            os.remove(db_path)
        except:
            pass
        fid_manager = FileIdManager(db_path=db_path)

        if not insert:
            return

        for i in range(n):
            fid_manager.con.execute(
                "INSERT INTO Files (path) VALUES (?)", (f"abracadabra/{i}.txt",)
            )
        fid_manager.con.commit()

    return setup


BATCH_SIZE = 100_000


def build_test_index(n, single_transaction, batched=False):
    def test_index():
        fid_manager = FileIdManager(db_path=db_path)

        if single_transaction:
            if batched:
                for batch_start in range(0, n, BATCH_SIZE):
                    batch_end = batch_start + BATCH_SIZE
                    fid_manager.con.execute(
                        "INSERT INTO FILES (path) VALUES "
                        + ",".join(
                            [f'("abracadabra/{i}.txt")' for i in range(batch_start, batch_end)]
                        )
                    )
            else:
                for i in range(n):
                    fid_manager.con.execute(
                        "INSERT INTO Files (path) VALUES (?)", (f"abracadabra/{i}.txt",)
                    )

            fid_manager.con.commit()
        else:
            for i in range(n):
                fid_manager.index(f"abracadabra/{i}.txt")

    return test_index


def test_copy():
    fid_manager = FileIdManager(db_path=db_path)
    fid_manager.copy("abracadabra", "shazam", recursive=True)


def test_move():
    fid_manager = FileIdManager(db_path=db_path)
    fid_manager.move("abracadabra", "shazam", recursive=True)


def test_delete():
    fid_manager = FileIdManager(db_path=db_path)
    fid_manager.delete("abracadabra", recursive=True)


row_template = "{:<9,d} files | {:<8.4f} s"


# too slow for 1k+
print("Index benchmark (separate transactions)")
for i in [100, 1_000]:
    print(
        row_template.format(
            i,
            timeit.timeit(
                build_test_index(i, single_transaction=False),
                build_setup(i, insert=False),
                number=1,
            ),
        )
    )

print("Index benchmark (single transaction, atomic INSERTs)")
for i in [100, 1_000, 10_000, 100_000, 1_000_000]:
    print(
        row_template.format(
            i,
            timeit.timeit(
                build_test_index(i, single_transaction=True, batched=False),
                build_setup(i, insert=False),
                number=1,
            ),
        )
    )

# suggested by https://stackoverflow.com/a/72527058/12548458
# asymptotically faster because it reduces work being done by the SQLite VDBE https://www.sqlite.org/opcode.html
# weird constant time factor that makes it sub-optimal for <1M records.
print("Index benchmark (single transaction, batched INSERTs)")
for i in [100, 1_000, 10_000, 100_000, 1_000_000]:
    print(
        row_template.format(
            i,
            timeit.timeit(
                build_test_index(i, single_transaction=True, batched=True),
                build_setup(i, insert=False),
                number=1,
            ),
        )
    )

print("Recursive move benchmark")
for i in [100, 1_000, 10_000, 100_000, 1_000_000]:
    print(row_template.format(i, timeit.timeit(test_move, build_setup(i), number=1)))

print("Recursive copy benchmark")
for i in [100, 1_000, 10_000, 100_000, 1_000_000]:
    print(row_template.format(i, timeit.timeit(test_copy, build_setup(i), number=1)))

print("Recursive delete benchmark")
for i in [100, 1_000, 10_000, 100_000, 1_000_000]:
    print(row_template.format(i, timeit.timeit(test_delete, build_setup(i), number=1)))
