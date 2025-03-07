const vscode = require("vscode");
const { exec } = require("child_process");
const path = require("path");

function activate(context) {
    let outputChannel = vscode.window.createOutputChannel("GOX Paser");

    let disposable = vscode.commands.registerCommand("extension.runFactorize", () => {
        vscode.window.showInformationMessage("Running Factorize!");

        const workspaceFolders = vscode.workspace.workspaceFolders;
        if (!workspaceFolders) {
            vscode.window.showErrorMessage("No workspace folder found!");
            return;
        }

        const projectPath = workspaceFolders[0].uri.fsPath;
        const lexerPath = path.join(projectPath, "lexer-parser-implementation.py");
        const fileToAnalyze = path.join(projectPath, "factorize.gox");

        // Run lexer.py with absolute paths
        exec(`python "${lexerPath}" "${fileToAnalyze}"`, { cwd: projectPath }, (error, stdout, stderr) => {
            if (error) {
                vscode.window.showErrorMessage(`Error: ${error.message}`);
                return;
            }
/*
            // Open output channel and print the tokens
            outputChannel.clear();
            outputChannel.appendLine("lexer-parser Output:");
            outputChannel.appendLine(stdout);
            outputChannel.show(true); // Show output panel*/
        });
    });

    context.subscriptions.push(disposable);
}

function deactivate() {}

module.exports = {
    activate,
    deactivate
};
