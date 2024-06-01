/*
Colab:
See https://gist.github.com/korakot/d10a43490f3da17d4915cdc1f200b180
*/


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


  if (Jupyter) {
    var python =
    `import climetlab.plotting.wms\nclimetlab.plotting.wms.direct_wms('${
        url}')\n`;
console.log('python', python);
Jupyter.notebook.kernel.execute(python, callbacks);
  }

  if (google) {
    var result = await google.colab.kernel.invokeFunction('direct_wms', [url], {});
    console.log('result', result);
  }

}, false);
