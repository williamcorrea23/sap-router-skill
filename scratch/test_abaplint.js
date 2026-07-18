const fs = require("fs");
const path = require("path");
const glob = require("glob");
const { Registry, Config, MemoryFile } = require("@abaplint/core");

async function run() {
  const configFilename = "templates/abaplint.json";
  const json = fs.readFileSync(configFilename, "utf8");
  const config = new Config(json);
  
  console.log("Config check_syntax rule configuration:", config.readByKey("rules", "check_syntax"));

  const base = "templates";
  const configFiles = config.get().global.files;
  const filesList = Array.isArray(configFiles) ? configFiles : [configFiles];
  let loaded = [];

  for (const l of filesList) {
    const globPattern = path.posix.join(base, l);
    const files = glob.sync(globPattern, { nodir: true, absolute: true, posix: true });
    
    for (let f of files) {
      if (f.startsWith("//?/")) {
        f = f.substring(4);
      }
      const content = fs.readFileSync(f, "utf8");
      
      let virtualFilename = f;
      if (f.endsWith("zcl_abap_repl_v2.clas.abap")) {
        virtualFilename = f.replace("zcl_abap_repl_v2.clas.abap", "zcl_abap_repl_v2.clas.abap");
      }
      
      loaded.push(new MemoryFile(f, content));
    }
  }

  const reg = new Registry(config);
  for (const file of loaded) {
    reg.addFile(file);
  }
  
  await reg.parseAsync();
  
  const issues = reg.findIssues();
  console.log("Total issues found:", issues.length);
  for (const issue of issues) {
    console.log(`- [${issue.getKey()}] ${issue.getMessage()} in ${issue.getFilename()}`);
  }
}

run().catch(console.error);
