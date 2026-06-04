const path = require("path");
const CopyWebpackPlugin = require("copy-webpack-plugin");

module.exports = {
  entry: {
    commands: "./src/commands/commands.js",
    taskpane: "./src/taskpane/taskpane.js",
  },
  output: {
    filename: "[name].js",
    path: path.resolve(__dirname, "dist"),
    clean: true,
  },
  devtool: "source-map",
  plugins: [
    new CopyWebpackPlugin({
      patterns: [
        { from: "src/commands/commands.html", to: "commands.html" },
        { from: "src/taskpane/taskpane.html", to: "taskpane.html" },
        { from: "src/taskpane/taskpane.css", to: "taskpane.css" },
        { from: "src/hello.html", to: "hello.html" },
        {
          from: "node_modules/@microsoft/office-js/dist/office.js",
          to: "office.js",
        },
        { from: "../mapping.json", to: "mapping.json" },
        { from: "assets", to: "assets" },
      ],
    }),
  ],
};
