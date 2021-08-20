module.exports = {
  entry: ["./simple_ext1/static/index.js"],
  output: {
    path: require("path").join(__dirname, "simple_ext1", "static"),
    filename: "bundle.js",
  },
  mode: "development",
};
