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
      };var element = document.getElementById("2e95a9c4-9a01-4f75-85c5-ad62731389d0");
      if (element == null) {
        console.log("Bokeh: ERROR: autoload.js configured with elementid '2e95a9c4-9a01-4f75-85c5-ad62731389d0' but no matching script tag was found. ")
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
                    
                  var docs_json = '{"f55c1a35-4c5d-467d-9f73-0ba62f3b350f":{"roots":{"references":[{"attributes":{"formatter":{"id":"17109862-bb3a-4bd5-a8a9-d40fc130f0bc","type":"BasicTickFormatter"},"plot":{"id":"f0544a0e-0d56-4f37-abe9-951c0f1c5965","subtype":"Figure","type":"Plot"},"ticker":{"id":"b86c6ea1-9529-499d-a842-5a8caf579444","type":"BasicTicker"}},"id":"9341a0de-4b45-443a-8ad4-d409aeb5718e","type":"LinearAxis"},{"attributes":{"data_source":{"id":"0a6da75e-06a2-4289-a5f6-36cc0cbca8a2","type":"ColumnDataSource"},"glyph":{"id":"36e5fd44-4051-471a-aa2a-bc27b6dba3ae","type":"Line"},"hover_glyph":null,"muted_glyph":null,"nonselection_glyph":{"id":"cc15962e-efcd-4a25-9372-1be5adbeec0f","type":"Line"},"selection_glyph":null,"view":{"id":"3bdf974c-2c8f-4b2e-8dfa-09c183fd5405","type":"CDSView"}},"id":"623c7b83-dd70-431f-a874-a4bca17e875a","type":"GlyphRenderer"},{"attributes":{},"id":"17109862-bb3a-4bd5-a8a9-d40fc130f0bc","type":"BasicTickFormatter"},{"attributes":{"below":[{"id":"0936096b-b93a-40b8-b447-9d1bbf272e0f","type":"LinearAxis"}],"left":[{"id":"9341a0de-4b45-443a-8ad4-d409aeb5718e","type":"LinearAxis"}],"plot_height":300,"plot_width":300,"renderers":[{"id":"0936096b-b93a-40b8-b447-9d1bbf272e0f","type":"LinearAxis"},{"id":"b958c6fa-4d9b-4abf-a773-58a27ee1e2b1","type":"Grid"},{"id":"9341a0de-4b45-443a-8ad4-d409aeb5718e","type":"LinearAxis"},{"id":"fcf8f0e7-b693-42a6-95d7-9c4c04881d3f","type":"Grid"},{"id":"a1f86269-2add-4dba-bddb-00e9d6629507","type":"BoxAnnotation"},{"id":"623c7b83-dd70-431f-a874-a4bca17e875a","type":"GlyphRenderer"},{"id":"cbf21444-0161-42e6-9f84-154e6ccb319a","type":"GlyphRenderer"}],"title":{"id":"aec94c41-986d-413f-bd0b-fb6d65e66f39","type":"Title"},"toolbar":{"id":"eaa29d16-74e5-4315-a4c2-e4a2b961e2a9","type":"Toolbar"},"x_range":{"id":"60208222-e14e-48b9-82ab-71e05c7370c7","type":"DataRange1d"},"x_scale":{"id":"cd5a909e-45f6-4f6b-8440-a564d5fdea69","type":"LinearScale"},"y_range":{"id":"c8ee8f62-185d-41bd-be38-c2f1b618aed1","type":"DataRange1d"},"y_scale":{"id":"ec142f43-8cba-43cf-ab62-96e18f6b3c9b","type":"LinearScale"}},"id":"f0544a0e-0d56-4f37-abe9-951c0f1c5965","subtype":"Figure","type":"Plot"},{"attributes":{},"id":"b86c6ea1-9529-499d-a842-5a8caf579444","type":"BasicTicker"},{"attributes":{"line_color":"#1f77b4","line_width":2,"x":{"field":"x"},"y":{"field":"y"}},"id":"36e5fd44-4051-471a-aa2a-bc27b6dba3ae","type":"Line"},{"attributes":{"dimension":1,"plot":{"id":"f0544a0e-0d56-4f37-abe9-951c0f1c5965","subtype":"Figure","type":"Plot"},"ticker":{"id":"b86c6ea1-9529-499d-a842-5a8caf579444","type":"BasicTicker"}},"id":"fcf8f0e7-b693-42a6-95d7-9c4c04881d3f","type":"Grid"},{"attributes":{"bottom_units":"screen","fill_alpha":{"value":0.5},"fill_color":{"value":"lightgrey"},"left_units":"screen","level":"overlay","line_alpha":{"value":1.0},"line_color":{"value":"black"},"line_dash":[4,4],"line_width":{"value":2},"plot":null,"render_mode":"css","right_units":"screen","top_units":"screen"},"id":"a1f86269-2add-4dba-bddb-00e9d6629507","type":"BoxAnnotation"},{"attributes":{"active_drag":"auto","active_inspect":"auto","active_scroll":"auto","active_tap":"auto","tools":[{"id":"5d579db8-a8f4-4f10-b27f-38d7a86e4553","type":"PanTool"},{"id":"e7fbdde7-b5f1-48a2-a768-7df08fa93a3f","type":"WheelZoomTool"},{"id":"f80be345-612a-475d-a0d6-b2488cf0214a","type":"BoxZoomTool"},{"id":"2494293d-0873-43f7-bd1d-00ba016b92c8","type":"SaveTool"},{"id":"58a0ee7b-23fb-4175-beba-3f134c40d89a","type":"ResetTool"},{"id":"477c708e-a8dd-417e-b532-8cb4acaac818","type":"HelpTool"}]},"id":"eaa29d16-74e5-4315-a4c2-e4a2b961e2a9","type":"Toolbar"},{"attributes":{"line_alpha":0.1,"line_color":"#1f77b4","line_width":2,"x":{"field":"x"},"y":{"field":"y"}},"id":"cc15962e-efcd-4a25-9372-1be5adbeec0f","type":"Line"},{"attributes":{"callback":null},"id":"c8ee8f62-185d-41bd-be38-c2f1b618aed1","type":"DataRange1d"},{"attributes":{},"id":"5d579db8-a8f4-4f10-b27f-38d7a86e4553","type":"PanTool"},{"attributes":{},"id":"e7fbdde7-b5f1-48a2-a768-7df08fa93a3f","type":"WheelZoomTool"},{"attributes":{"overlay":{"id":"a1f86269-2add-4dba-bddb-00e9d6629507","type":"BoxAnnotation"}},"id":"f80be345-612a-475d-a0d6-b2488cf0214a","type":"BoxZoomTool"},{"attributes":{},"id":"cd5a909e-45f6-4f6b-8440-a564d5fdea69","type":"LinearScale"},{"attributes":{},"id":"2494293d-0873-43f7-bd1d-00ba016b92c8","type":"SaveTool"},{"attributes":{"callback":null,"column_names":["x","y"],"data":{"x":[1,2,3,4,5],"y":[6,7,6,4,5]},"selected":null,"selection_policy":null},"id":"0a6da75e-06a2-4289-a5f6-36cc0cbca8a2","type":"ColumnDataSource"},{"attributes":{},"id":"58a0ee7b-23fb-4175-beba-3f134c40d89a","type":"ResetTool"},{"attributes":{},"id":"477c708e-a8dd-417e-b532-8cb4acaac818","type":"HelpTool"},{"attributes":{},"id":"ca43d66a-67ac-404e-90f6-2238c84a80a4","type":"BasicTickFormatter"},{"attributes":{"callback":null,"column_names":["x","y"],"data":{"x":[1,2,3,4,5],"y":[6,7,6,4,5]},"selected":null,"selection_policy":null},"id":"7df0fda3-1c3a-407f-8b6d-571192ca10b8","type":"ColumnDataSource"},{"attributes":{"source":{"id":"0a6da75e-06a2-4289-a5f6-36cc0cbca8a2","type":"ColumnDataSource"}},"id":"3bdf974c-2c8f-4b2e-8dfa-09c183fd5405","type":"CDSView"},{"attributes":{"data_source":{"id":"7df0fda3-1c3a-407f-8b6d-571192ca10b8","type":"ColumnDataSource"},"glyph":{"id":"114796a6-f0d5-44b6-8b98-32a94d2d1c8b","type":"Circle"},"hover_glyph":null,"muted_glyph":null,"nonselection_glyph":{"id":"2f75d0fa-c205-4758-b3ef-c966884bece6","type":"Circle"},"selection_glyph":null,"view":{"id":"41da7313-b614-4151-99da-87e9eb8d1c6c","type":"CDSView"}},"id":"cbf21444-0161-42e6-9f84-154e6ccb319a","type":"GlyphRenderer"},{"attributes":{"fill_color":{"value":"white"},"line_color":{"value":"#1f77b4"},"size":{"units":"screen","value":10},"x":{"field":"x"},"y":{"field":"y"}},"id":"114796a6-f0d5-44b6-8b98-32a94d2d1c8b","type":"Circle"},{"attributes":{"fill_alpha":{"value":0.1},"fill_color":{"value":"#1f77b4"},"line_alpha":{"value":0.1},"line_color":{"value":"#1f77b4"},"size":{"units":"screen","value":10},"x":{"field":"x"},"y":{"field":"y"}},"id":"2f75d0fa-c205-4758-b3ef-c966884bece6","type":"Circle"},{"attributes":{"source":{"id":"7df0fda3-1c3a-407f-8b6d-571192ca10b8","type":"ColumnDataSource"}},"id":"41da7313-b614-4151-99da-87e9eb8d1c6c","type":"CDSView"},{"attributes":{},"id":"ec142f43-8cba-43cf-ab62-96e18f6b3c9b","type":"LinearScale"},{"attributes":{"callback":null},"id":"60208222-e14e-48b9-82ab-71e05c7370c7","type":"DataRange1d"},{"attributes":{"formatter":{"id":"ca43d66a-67ac-404e-90f6-2238c84a80a4","type":"BasicTickFormatter"},"plot":{"id":"f0544a0e-0d56-4f37-abe9-951c0f1c5965","subtype":"Figure","type":"Plot"},"ticker":{"id":"6417247a-6db3-4dc0-a91a-9507227d58c2","type":"BasicTicker"}},"id":"0936096b-b93a-40b8-b447-9d1bbf272e0f","type":"LinearAxis"},{"attributes":{"plot":{"id":"f0544a0e-0d56-4f37-abe9-951c0f1c5965","subtype":"Figure","type":"Plot"},"ticker":{"id":"6417247a-6db3-4dc0-a91a-9507227d58c2","type":"BasicTicker"}},"id":"b958c6fa-4d9b-4abf-a773-58a27ee1e2b1","type":"Grid"},{"attributes":{"plot":null,"text":"example_bokeh"},"id":"aec94c41-986d-413f-bd0b-fb6d65e66f39","type":"Title"},{"attributes":{},"id":"6417247a-6db3-4dc0-a91a-9507227d58c2","type":"BasicTicker"}],"root_ids":["f0544a0e-0d56-4f37-abe9-951c0f1c5965"]},"title":"Bokeh Application","version":"0.12.15"}}';
                  var render_items = [{"docid":"f55c1a35-4c5d-467d-9f73-0ba62f3b350f","elementid":"2e95a9c4-9a01-4f75-85c5-ad62731389d0","modelid":"f0544a0e-0d56-4f37-abe9-951c0f1c5965"}];
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