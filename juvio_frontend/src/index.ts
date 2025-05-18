import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

import { ILauncher } from '@jupyterlab/launcher';


const plugin: JupyterFrontEndPlugin<void> = {
  id: 'juvio_frontend:plugin',
  description: 'Juvio JupyterLab extension',
  autoStart: true,
  requires: [ILauncher],
  activate: (
    app: JupyterFrontEnd,
    launcher: ILauncher
  ) => {
    console.log('JupyterLab extension juvio_frontend is activated!');

    app.docRegistry.addFileType({
      name: 'juvio',
      displayName: 'Juvio Notebook',
      extensions: ['.juvio'],
      contentType: 'notebook',
      fileFormat: 'json',
    });

    app.docRegistry.addFileType({
      name: 'notebook',
      extensions: ['.juvio']
    });

    const { commands } = app;
    commands.addCommand('create-juvio-file', {
      label: 'Juvio Notebook',
      execute: () => {
        return commands.execute('docmanager:new-untitled', {
          type: 'file',
          ext: '.juvio',
          kernelName: "juvio",
        });
      }
    });

    launcher.add({
      category: 'Notebook',
      rank: 1,
      command: 'create-juvio-file',
      kernelIconUrl: 'https://gist.githubusercontent.com/OKUA1/d6e65e883546021ea774857878fd0537/raw/4de2ea217e25d9ff7b3d2a73899e85665ed7d94c/juvio_logo.svg',
    });
  }
};

export default plugin;
