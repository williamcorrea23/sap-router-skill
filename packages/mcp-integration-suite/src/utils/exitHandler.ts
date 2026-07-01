import { rimrafSync } from "rimraf";
import { logInfo, projPath } from "..";
import path from "path";

export const registerDeleteTempOnExit = () => {

    const deleteTemp = () => {
        rimrafSync(path.join(projPath, 'temp'))
    }

    process.on("exit", (code) => {
        logInfo('Exit event triggered. Deleting temp folder')
        deleteTemp()
    });

    // just in case some user like using "kill"
    process.on("SIGTERM", (signal) => {
        logInfo(`Process ${process.pid} received a SIGTERM signal`);
        deleteTemp()
    });

    // catch ctrl-c, so that event 'exit' always works
    process.on("SIGINT", (signal) => {
        logInfo(`Process ${process.pid} has been interrupted`);
        logInfo('Exit event triggered. Deleting temp folder')
        deleteTemp()
        process.exit(0);
    });

}