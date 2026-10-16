const path = require("path");
const fs = require("fs");
const webpack = require("webpack");
const CopyWebpackPlugin = require("copy-webpack-plugin");

const pkg = require("./package.json");
const manifestXml = fs.readFileSync(
  path.join(__dirname, "manifest.xml"),
  "utf8"
);
const manifestMatch = manifestXml.match(/<Version>([^<]+)<\/Version>/);
const wordManifest = manifestMatch ? manifestMatch[1] : "0.0.0.0";

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
    new webpack.DefinePlugin({
      __MM_WORD_VERSION__: JSON.stringify(pkg.version),
      __MM_WORD_MANIFEST__: JSON.stringify(wordManifest),
      __MM_VERSION_JSON_URL__: JSON.stringify(
        "https://marinamoji.github.io/plugin/version.json"
      ),
    }),
    new CopyWebpackPlugin({
      patterns: [
        { from: "src/commands/commands.html", to: "commands.html" },
        { from: "src/taskpane/taskpane.html", to: "taskpane.html" },
        { from: "src/taskpane/taskpane.css", to: "taskpane.css" },
        { from: "src/hello.html", to: "hello.html" },
        /* Office.js must come from Microsoft CDN in production (Marketplace FAQ). */
        { from: "../mapping.json", to: "mapping.json" },
        { from: "assets", to: "assets" },
      ],
    }),
  ],
};
