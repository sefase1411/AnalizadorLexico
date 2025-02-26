const vscode = require('vscode');

function activate(context) {
    let disposable = vscode.commands.registerCommand('gox.run', function () {
        vscode.window.showInformationMessage('GOX Run ejecutado!');
    });

    context.subscriptions.push(disposable);
}

function deactivate() {}

module.exports = {
    activate,
    deactivate
};
