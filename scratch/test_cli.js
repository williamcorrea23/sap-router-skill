const { run } = require("../node_modules/@abaplint/cli/build/cli.js");

async function test() {
  const args = {
    configFilename: "templates/abaplint.json"
  };
  console.log("Calling run with args:", args);
  const result = await run(args);
  console.log("Run finished!");
  console.log("Result output:", result.output);
  console.log("Issues count:", result.issues.length);
  console.log("Registry files count:", result.reg ? result.reg.getFiles().length : "N/A");
}

test().catch(console.error);
