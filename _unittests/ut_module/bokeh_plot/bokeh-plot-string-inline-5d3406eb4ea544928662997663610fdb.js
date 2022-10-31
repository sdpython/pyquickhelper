(function() {
  var fn = function() {
    
    (function(root) {
      function now() {
        return new Date();
      }
    
      var force = false;
    
      if (typeof (root._bokeh_onload_callbacks) === "undefined" || force === true) {
        root._bokeh_onload_callbacks = [];
        root._bokeh_is_loading = undefined;
      }
    
      
      
    
      
      
    
      function run_callbacks() {
        try {
          root._bokeh_onload_callbacks.forEach(function(callback) { callback() });
        }
        finally {
          delete root._bokeh_onload_callbacks
        }
        console.info("Bokeh: all callbacks have finished");
      }
    
      function load_libs(js_urls, callback) {
        root._bokeh_onload_callbacks.push(callback);
        if (root._bokeh_is_loading > 0) {
          console.log("Bokeh: BokehJS is being loaded, scheduling callback at", now());
          return null;
        }
        if (js_urls == null || js_urls.length === 0) {
          run_callbacks();
          return null;
        }
        console.log("Bokeh: BokehJS not loaded, scheduling load and callback at", now());
        root._bokeh_is_loading = js_urls.length;
        for (var i = 0; i < js_urls.length; i++) {
          var url = js_urls[i];
          var s = document.createElement('script');
          s.src = url;
          s.async = false;
          s.onreadystatechange = s.onload = function() {
            root._bokeh_is_loading--;
            if (root._bokeh_is_loading === 0) {
              console.log("Bokeh: all BokehJS libraries loaded");
              run_callbacks()
            }
          };
          s.onerror = function() {
            console.warn("failed to load library " + url);
          };
          console.log("Bokeh: injecting script tag for BokehJS library: ", url);
          document.getElementsByTagName("head")[0].appendChild(s);
        }
      };var element = document.getElementById("581105d0-7f9d-44ac-88ef-a9c390b2dad1");
      if (element == null) {
        console.log("Bokeh: ERROR: autoload.js configured with elementid '581105d0-7f9d-44ac-88ef-a9c390b2dad1' but no matching script tag was found. ")
        return false;
      }
    
      var js_urls = ["https://cdn.pydata.org/bokeh/release/bokeh-0.12.15.min.js", "https://cdn.pydata.org/bokeh/release/bokeh-widgets-0.12.15.min.js", "https://cdn.pydata.org/bokeh/release/bokeh-tables-0.12.15.min.js", "https://cdn.pydata.org/bokeh/release/bokeh-gl-0.12.15.min.js"];
    
      var inline_js = [
        function(Bokeh) {
          Bokeh.set_log_level("info");
        },
        
        function(Bokeh) {
          
        },
        
        function(Bokeh) {
          (function() {
            var fn = function() {
              Bokeh.safely(function() {
                (function(root) {
                  function embed_document(root) {
                    
                  var docs_json = '{"31ef4c7a-a62f-480a-8e1b-49e75bc3041a":{"roots":{"references":[{"attributes":{},"id":"a699a0d6-e3bf-477f-a653-6a6bb35bd5b9","type":"BasicTicker"},{"attributes":{"line_alpha":0.1,"line_color":"#1f77b4","line_width":2,"x":{"field":"x"},"y":{"field":"y"}},"id":"dad0d3fd-50c8-4dff-890b-51bf79acc00b","type":"Line"},{"attributes":{"line_color":"#1f77b4","line_width":2,"x":{"field":"x"},"y":{"field":"y"}},"id":"a69759f7-9217-4a19-89bf-36d00df3daf3","type":"Line"},{"attributes":{"below":[{"id":"ffda3082-7fd8-44ed-99fa-2a09c95ae271","type":"LinearAxis"}],"left":[{"id":"a161d923-65c2-465f-b19b-284ba06d4eaf","type":"LinearAxis"}],"plot_height":300,"plot_width":300,"renderers":[{"id":"ffda3082-7fd8-44ed-99fa-2a09c95ae271","type":"LinearAxis"},{"id":"514274cb-3da5-4652-9239-f6dfde5416a4","type":"Grid"},{"id":"a161d923-65c2-465f-b19b-284ba06d4eaf","type":"LinearAxis"},{"id":"18373b9b-2ae8-4481-9285-1f5244fb17f6","type":"Grid"},{"id":"3626e6a8-8786-462b-81c9-d9eb6a400d1f","type":"BoxAnnotation"},{"id":"1bc6b8f1-4eca-493d-9a02-470eafb48b59","type":"GlyphRenderer"},{"id":"f683b4c6-7e7f-4a5e-ba11-d4960cb36552","type":"GlyphRenderer"}],"title":{"id":"6d158f75-bb4f-4bba-87f7-67dfd7c577d2","type":"Title"},"toolbar":{"id":"4537f6e4-ef41-4fd1-acce-770f988b394d","type":"Toolbar"},"x_range":{"id":"08f23546-9502-4a1e-ab88-9fd1c3981e74","type":"DataRange1d"},"x_scale":{"id":"a41233ef-4787-48e1-b4d2-577113987701","type":"LinearScale"},"y_range":{"id":"2c05c6db-c768-47b8-ab4f-cf1a4ab2d983","type":"DataRange1d"},"y_scale":{"id":"202e917e-b4d5-4601-af03-196ffe8eb212","type":"LinearScale"}},"id":"b2e12950-6141-42b1-83e8-a9328ad37706","subtype":"Figure","type":"Plot"},{"attributes":{"dimension":1,"plot":{"id":"b2e12950-6141-42b1-83e8-a9328ad37706","subtype":"Figure","type":"Plot"},"ticker":{"id":"a699a0d6-e3bf-477f-a653-6a6bb35bd5b9","type":"BasicTicker"}},"id":"18373b9b-2ae8-4481-9285-1f5244fb17f6","type":"Grid"},{"attributes":{"source":{"id":"1b858297-af17-4999-aa5d-9e6e9abd888c","type":"ColumnDataSource"}},"id":"316b2827-ce2f-448e-b855-52e97e7bc7c0","type":"CDSView"},{"attributes":{"bottom_units":"screen","fill_alpha":{"value":0.5},"fill_color":{"value":"lightgrey"},"left_units":"screen","level":"overlay","line_alpha":{"value":1.0},"line_color":{"value":"black"},"line_dash":[4,4],"line_width":{"value":2},"plot":null,"render_mode":"css","right_units":"screen","top_units":"screen"},"id":"3626e6a8-8786-462b-81c9-d9eb6a400d1f","type":"BoxAnnotation"},{"attributes":{"active_drag":"auto","active_inspect":"auto","active_scroll":"auto","active_tap":"auto","tools":[{"id":"05d4591f-4f2b-4e35-9272-60c23f903190","type":"PanTool"},{"id":"8c145530-a2a4-487e-8aa6-b3697b7ad1ba","type":"WheelZoomTool"},{"id":"5ca3a5a5-b32a-4f1c-8685-532852925979","type":"BoxZoomTool"},{"id":"a629f11d-360e-4bfd-b96f-8e42acabfccb","type":"SaveTool"},{"id":"39539011-2303-48f4-9e5b-88e183fdea49","type":"ResetTool"},{"id":"4550a0d1-ddab-4e23-8fa6-2678e16dc5e1","type":"HelpTool"}]},"id":"4537f6e4-ef41-4fd1-acce-770f988b394d","type":"Toolbar"},{"attributes":{},"id":"c9f27d89-6e72-4bd6-a769-606d523f813f","type":"BasicTickFormatter"},{"attributes":{},"id":"14bdf4ef-165a-4c9b-9938-0ef160ff9b69","type":"BasicTickFormatter"},{"attributes":{},"id":"05d4591f-4f2b-4e35-9272-60c23f903190","type":"PanTool"},{"attributes":{"callback":null},"id":"2c05c6db-c768-47b8-ab4f-cf1a4ab2d983","type":"DataRange1d"},{"attributes":{},"id":"8c145530-a2a4-487e-8aa6-b3697b7ad1ba","type":"WheelZoomTool"},{"attributes":{"overlay":{"id":"3626e6a8-8786-462b-81c9-d9eb6a400d1f","type":"BoxAnnotation"}},"id":"5ca3a5a5-b32a-4f1c-8685-532852925979","type":"BoxZoomTool"},{"attributes":{},"id":"a629f11d-360e-4bfd-b96f-8e42acabfccb","type":"SaveTool"},{"attributes":{},"id":"a41233ef-4787-48e1-b4d2-577113987701","type":"LinearScale"},{"attributes":{},"id":"39539011-2303-48f4-9e5b-88e183fdea49","type":"ResetTool"},{"attributes":{},"id":"4550a0d1-ddab-4e23-8fa6-2678e16dc5e1","type":"HelpTool"},{"attributes":{"callback":null,"column_names":["x","y"],"data":{"x":[1,2,3,4,5],"y":[6,7,6,4,5]},"selected":null,"selection_policy":null},"id":"1b858297-af17-4999-aa5d-9e6e9abd888c","type":"ColumnDataSource"},{"attributes":{"fill_color":{"value":"white"},"line_color":{"value":"#1f77b4"},"size":{"units":"screen","value":10},"x":{"field":"x"},"y":{"field":"y"}},"id":"24096b49-9856-4259-b57b-9ae611ba961b","type":"Circle"},{"attributes":{"callback":null,"column_names":["x","y"],"data":{"x":[1,2,3,4,5],"y":[6,7,6,4,5]},"selected":null,"selection_policy":null},"id":"e58b5c9b-1bd2-4737-99a8-5106d81547d9","type":"ColumnDataSource"},{"attributes":{"source":{"id":"e58b5c9b-1bd2-4737-99a8-5106d81547d9","type":"ColumnDataSource"}},"id":"de482937-bd71-4fce-b830-e91fe554ad8e","type":"CDSView"},{"attributes":{"data_source":{"id":"e58b5c9b-1bd2-4737-99a8-5106d81547d9","type":"ColumnDataSource"},"glyph":{"id":"24096b49-9856-4259-b57b-9ae611ba961b","type":"Circle"},"hover_glyph":null,"muted_glyph":null,"nonselection_glyph":{"id":"97e6adb6-1c40-4632-8002-01aaf4ff8494","type":"Circle"},"selection_glyph":null,"view":{"id":"de482937-bd71-4fce-b830-e91fe554ad8e","type":"CDSView"}},"id":"f683b4c6-7e7f-4a5e-ba11-d4960cb36552","type":"GlyphRenderer"},{"attributes":{"fill_alpha":{"value":0.1},"fill_color":{"value":"#1f77b4"},"line_alpha":{"value":0.1},"line_color":{"value":"#1f77b4"},"size":{"units":"screen","value":10},"x":{"field":"x"},"y":{"field":"y"}},"id":"97e6adb6-1c40-4632-8002-01aaf4ff8494","type":"Circle"},{"attributes":{"data_source":{"id":"1b858297-af17-4999-aa5d-9e6e9abd888c","type":"ColumnDataSource"},"glyph":{"id":"a69759f7-9217-4a19-89bf-36d00df3daf3","type":"Line"},"hover_glyph":null,"muted_glyph":null,"nonselection_glyph":{"id":"dad0d3fd-50c8-4dff-890b-51bf79acc00b","type":"Line"},"selection_glyph":null,"view":{"id":"316b2827-ce2f-448e-b855-52e97e7bc7c0","type":"CDSView"}},"id":"1bc6b8f1-4eca-493d-9a02-470eafb48b59","type":"GlyphRenderer"},{"attributes":{},"id":"202e917e-b4d5-4601-af03-196ffe8eb212","type":"LinearScale"},{"attributes":{"callback":null},"id":"08f23546-9502-4a1e-ab88-9fd1c3981e74","type":"DataRange1d"},{"attributes":{"formatter":{"id":"c9f27d89-6e72-4bd6-a769-606d523f813f","type":"BasicTickFormatter"},"plot":{"id":"b2e12950-6141-42b1-83e8-a9328ad37706","subtype":"Figure","type":"Plot"},"ticker":{"id":"9b6d9402-76c7-4f53-97a7-65bc5e72557e","type":"BasicTicker"}},"id":"ffda3082-7fd8-44ed-99fa-2a09c95ae271","type":"LinearAxis"},{"attributes":{"formatter":{"id":"14bdf4ef-165a-4c9b-9938-0ef160ff9b69","type":"BasicTickFormatter"},"plot":{"id":"b2e12950-6141-42b1-83e8-a9328ad37706","subtype":"Figure","type":"Plot"},"ticker":{"id":"a699a0d6-e3bf-477f-a653-6a6bb35bd5b9","type":"BasicTicker"}},"id":"a161d923-65c2-465f-b19b-284ba06d4eaf","type":"LinearAxis"},{"attributes":{},"id":"9b6d9402-76c7-4f53-97a7-65bc5e72557e","type":"BasicTicker"},{"attributes":{"plot":null,"text":"example_bokeh"},"id":"6d158f75-bb4f-4bba-87f7-67dfd7c577d2","type":"Title"},{"attributes":{"plot":{"id":"b2e12950-6141-42b1-83e8-a9328ad37706","subtype":"Figure","type":"Plot"},"ticker":{"id":"9b6d9402-76c7-4f53-97a7-65bc5e72557e","type":"BasicTicker"}},"id":"514274cb-3da5-4652-9239-f6dfde5416a4","type":"Grid"}],"root_ids":["b2e12950-6141-42b1-83e8-a9328ad37706"]},"title":"Bokeh Application","version":"0.12.15"}}';
                  var render_items = [{"docid":"31ef4c7a-a62f-480a-8e1b-49e75bc3041a","elementid":"581105d0-7f9d-44ac-88ef-a9c390b2dad1","modelid":"b2e12950-6141-42b1-83e8-a9328ad37706"}];
                  root.Bokeh.embed.embed_items(docs_json, render_items);
                
                  }
                  if (root.Bokeh !== undefined) {
                    embed_document(root);
                  } else {
                    var attempts = 0;
                    var timer = setInterval(function(root) {
                      if (root.Bokeh !== undefined) {
                        embed_document(root);
                        clearInterval(timer);
                      }
                      attempts++;
                      if (attempts > 100) {
                        console.log("Bokeh: ERROR: Unable to run BokehJS code because BokehJS library is missing")
                        clearInterval(timer);
                      }
                    }, 10, root)
                  }
                })(window);
              });
            };
            if (document.readyState != "loading") fn();
            else document.addEventListener("DOMContentLoaded", fn);
          })();
        },
        function(Bokeh) {
          console.log("Bokeh: injecting CSS: https://cdn.pydata.org/bokeh/release/bokeh-0.12.15.min.css");
          Bokeh.embed.inject_css("https://cdn.pydata.org/bokeh/release/bokeh-0.12.15.min.css");
          console.log("Bokeh: injecting CSS: https://cdn.pydata.org/bokeh/release/bokeh-widgets-0.12.15.min.css");
          Bokeh.embed.inject_css("https://cdn.pydata.org/bokeh/release/bokeh-widgets-0.12.15.min.css");
          console.log("Bokeh: injecting CSS: https://cdn.pydata.org/bokeh/release/bokeh-tables-0.12.15.min.css");
          Bokeh.embed.inject_css("https://cdn.pydata.org/bokeh/release/bokeh-tables-0.12.15.min.css");
        }
      ];
    
      function run_inline_js() {
        
        for (var i = 0; i < inline_js.length; i++) {
          inline_js[i].call(root, root.Bokeh);
        }
        
      }
    
      if (root._bokeh_is_loading === 0) {
        console.log("Bokeh: BokehJS loaded, going straight to plotting");
        run_inline_js();
      } else {
        load_libs(js_urls, function() {
          console.log("Bokeh: BokehJS plotting callback run at", now());
          run_inline_js();
        });
      }
    }(window));
  };
  if (document.readyState != "loading") fn();
  else document.addEventListener("DOMContentLoaded", fn);
})();