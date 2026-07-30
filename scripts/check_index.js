const fs = require("fs");

const html = fs.readFileSync("index.html", "utf8");
const scripts = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)];
for (const script of scripts) {
  new Function(script[1]);
}
const cards = [...html.matchAll(/id="slide-(D[12])-(\d+)"/g)];
console.log(`JavaScript syntax OK; ${scripts.length} script; ${cards.length} slide cards`);
