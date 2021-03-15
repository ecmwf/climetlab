window.document.addEventListener('direct-wms', function(e) {
  console.log('direct-wms', e.detail);



  var url = e.detail.url;

  var callbacks = {
    iopub: {
      output: function(data) {
        var error = null;

        if (data.msg_type == 'error') {
          error = data.content.ename + ': ' + data.content.evalue;
        }

        if (data.msg_type == 'stream') {
          e.detail.tile.src = data.content.text;
        }

        e.detail.done(error, e.detail.tile);
      }
    }
  };

  var python =
      `import climetlab.plotting.wms\nclimetlab.plotting.wms.direct_wms('${
          url}')\n`;
  console.log('python', python);
  Jupyter.notebook.kernel.execute(python, callbacks);
}, false);
