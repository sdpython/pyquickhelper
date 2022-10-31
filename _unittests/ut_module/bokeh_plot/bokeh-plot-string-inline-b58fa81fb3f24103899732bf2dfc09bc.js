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
      };var element = document.getElementById("6181baa2-189d-4f05-a8cd-2adc9a039595");
      if (element == null) {
        console.log("Bokeh: ERROR: autoload.js configured with elementid '6181baa2-189d-4f05-a8cd-2adc9a039595' but no matching script tag was found. ")
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
                    
                  var docs_json = '{"c79b14f6-fb9d-41f6-ad2c-19eca539532e":{"roots":{"references":[{"attributes":{},"id":"dbbb94f7-98bf-4771-a679-44eb341e818d","type":"PanTool"},{"attributes":{"data_source":{"id":"265efea6-02a3-48dc-8701-a79cfe1413c5","type":"ColumnDataSource"},"glyph":{"id":"45a395ae-155c-4d12-a858-32b3a97718a2","type":"Line"},"hover_glyph":null,"muted_glyph":null,"nonselection_glyph":{"id":"f472f272-8446-48cd-9a6b-71c543358662","type":"Line"},"selection_glyph":null,"view":{"id":"f3cc68d9-5b9b-4e0e-8895-d04117f818e0","type":"CDSView"}},"id":"b2153637-652c-4d1f-b760-33c30a3a8ba2","type":"GlyphRenderer"},{"attributes":{},"id":"a8f66553-73cf-4d9a-a96c-0f68a9702642","type":"LinearScale"},{"attributes":{},"id":"82632d54-972d-41ea-b984-3035e177e86e","type":"WheelZoomTool"},{"attributes":{"line_alpha":0.1,"line_color":"#1f77b4","line_width":2,"x":{"field":"x"},"y":{"field":"y"}},"id":"f472f272-8446-48cd-9a6b-71c543358662","type":"Line"},{"attributes":{"plot":null,"text":"example_bokeh"},"id":"e7bcbcb7-5bae-4611-bd41-532be6cd7ea2","type":"Title"},{"attributes":{"overlay":{"id":"4232321c-0bd8-44c0-9534-86250766faf8","type":"BoxAnnotation"}},"id":"d023d32e-9550-4473-b077-72010d70503b","type":"BoxZoomTool"},{"attributes":{},"id":"2df367bf-986f-478c-9d8b-8a073534ddf2","type":"SaveTool"},{"attributes":{},"id":"f3cb5067-9d73-4eab-b452-3889cb7eaa67","type":"LinearScale"},{"attributes":{},"id":"d2a4d48f-b0f5-4b91-ad35-5ec9e7b388b6","type":"ResetTool"},{"attributes":{},"id":"db561787-3bc4-46d7-99d1-60c224253e01","type":"HelpTool"},{"attributes":{},"id":"3cc8a07e-5185-416e-ac96-022fec50f8e0","type":"BasicTickFormatter"},{"attributes":{"fill_alpha":{"value":0.1},"fill_color":{"value":"#1f77b4"},"line_alpha":{"value":0.1},"line_color":{"value":"#1f77b4"},"size":{"units":"screen","value":10},"x":{"field":"x"},"y":{"field":"y"}},"id":"c5c3a43f-a090-4f17-96e7-e68afd6ea998","type":"Circle"},{"attributes":{"data_source":{"id":"dfd7d227-e62f-4fdd-9fba-4c13bf511327","type":"ColumnDataSource"},"glyph":{"id":"35b16bae-37c3-4085-8560-4f837bdd35eb","type":"Circle"},"hover_glyph":null,"muted_glyph":null,"nonselection_glyph":{"id":"c5c3a43f-a090-4f17-96e7-e68afd6ea998","type":"Circle"},"selection_glyph":null,"view":{"id":"c217756d-fe4a-4245-9f94-389b04a5a1cd","type":"CDSView"}},"id":"da979247-b20e-4d48-89c7-ca8ac7d1ba42","type":"GlyphRenderer"},{"attributes":{"callback":null,"column_names":["x","y"],"data":{"x":[1,2,3,4,5],"y":[6,7,6,4,5]},"selected":null,"selection_policy":null},"id":"dfd7d227-e62f-4fdd-9fba-4c13bf511327","type":"ColumnDataSource"},{"attributes":{"source":{"id":"dfd7d227-e62f-4fdd-9fba-4c13bf511327","type":"ColumnDataSource"}},"id":"c217756d-fe4a-4245-9f94-389b04a5a1cd","type":"CDSView"},{"attributes":{"source":{"id":"265efea6-02a3-48dc-8701-a79cfe1413c5","type":"ColumnDataSource"}},"id":"f3cc68d9-5b9b-4e0e-8895-d04117f818e0","type":"CDSView"},{"attributes":{"callback":null},"id":"f3ace1a2-0573-4bf0-9843-3b0b33d583e3","type":"DataRange1d"},{"attributes":{"plot":{"id":"8939ed4b-ea10-41e3-a20c-b37cbe1209a2","subtype":"Figure","type":"Plot"},"ticker":{"id":"c034c115-52de-4a2e-8350-77218673f224","type":"BasicTicker"}},"id":"2038128e-3f35-4384-b247-b51d53998f42","type":"Grid"},{"attributes":{"formatter":{"id":"1d0a4b09-edc5-4fbb-9d69-efb6a7340323","type":"BasicTickFormatter"},"plot":{"id":"8939ed4b-ea10-41e3-a20c-b37cbe1209a2","subtype":"Figure","type":"Plot"},"ticker":{"id":"c342f708-8fc9-441b-adfb-0df3494d560e","type":"BasicTicker"}},"id":"fd2f1d75-cf1a-42e3-98b7-f1d2b842eec3","type":"LinearAxis"},{"attributes":{"callback":null},"id":"01d25dff-1cd4-4782-9b24-c0762d035fac","type":"DataRange1d"},{"attributes":{"line_color":"#1f77b4","line_width":2,"x":{"field":"x"},"y":{"field":"y"}},"id":"45a395ae-155c-4d12-a858-32b3a97718a2","type":"Line"},{"attributes":{"below":[{"id":"3a2c5c74-dd08-4999-9781-c602de496417","type":"LinearAxis"}],"left":[{"id":"fd2f1d75-cf1a-42e3-98b7-f1d2b842eec3","type":"LinearAxis"}],"plot_height":300,"plot_width":300,"renderers":[{"id":"3a2c5c74-dd08-4999-9781-c602de496417","type":"LinearAxis"},{"id":"2038128e-3f35-4384-b247-b51d53998f42","type":"Grid"},{"id":"fd2f1d75-cf1a-42e3-98b7-f1d2b842eec3","type":"LinearAxis"},{"id":"4dcf4d13-091d-48bc-a2ee-f8c13853e865","type":"Grid"},{"id":"4232321c-0bd8-44c0-9534-86250766faf8","type":"BoxAnnotation"},{"id":"b2153637-652c-4d1f-b760-33c30a3a8ba2","type":"GlyphRenderer"},{"id":"da979247-b20e-4d48-89c7-ca8ac7d1ba42","type":"GlyphRenderer"}],"title":{"id":"e7bcbcb7-5bae-4611-bd41-532be6cd7ea2","type":"Title"},"toolbar":{"id":"28fe19c5-1002-48a1-a710-440e09186ccf","type":"Toolbar"},"x_range":{"id":"01d25dff-1cd4-4782-9b24-c0762d035fac","type":"DataRange1d"},"x_scale":{"id":"f3cb5067-9d73-4eab-b452-3889cb7eaa67","type":"LinearScale"},"y_range":{"id":"f3ace1a2-0573-4bf0-9843-3b0b33d583e3","type":"DataRange1d"},"y_scale":{"id":"a8f66553-73cf-4d9a-a96c-0f68a9702642","type":"LinearScale"}},"id":"8939ed4b-ea10-41e3-a20c-b37cbe1209a2","subtype":"Figure","type":"Plot"},{"attributes":{"formatter":{"id":"3cc8a07e-5185-416e-ac96-022fec50f8e0","type":"BasicTickFormatter"},"plot":{"id":"8939ed4b-ea10-41e3-a20c-b37cbe1209a2","subtype":"Figure","type":"Plot"},"ticker":{"id":"c034c115-52de-4a2e-8350-77218673f224","type":"BasicTicker"}},"id":"3a2c5c74-dd08-4999-9781-c602de496417","type":"LinearAxis"},{"attributes":{"fill_color":{"value":"white"},"line_color":{"value":"#1f77b4"},"size":{"units":"screen","value":10},"x":{"field":"x"},"y":{"field":"y"}},"id":"35b16bae-37c3-4085-8560-4f837bdd35eb","type":"Circle"},{"attributes":{"active_drag":"auto","active_inspect":"auto","active_scroll":"auto","active_tap":"auto","tools":[{"id":"dbbb94f7-98bf-4771-a679-44eb341e818d","type":"PanTool"},{"id":"82632d54-972d-41ea-b984-3035e177e86e","type":"WheelZoomTool"},{"id":"d023d32e-9550-4473-b077-72010d70503b","type":"BoxZoomTool"},{"id":"2df367bf-986f-478c-9d8b-8a073534ddf2","type":"SaveTool"},{"id":"d2a4d48f-b0f5-4b91-ad35-5ec9e7b388b6","type":"ResetTool"},{"id":"db561787-3bc4-46d7-99d1-60c224253e01","type":"HelpTool"}]},"id":"28fe19c5-1002-48a1-a710-440e09186ccf","type":"Toolbar"},{"attributes":{},"id":"c034c115-52de-4a2e-8350-77218673f224","type":"BasicTicker"},{"attributes":{"callback":null,"column_names":["x","y"],"data":{"x":[1,2,3,4,5],"y":[6,7,6,4,5]},"selected":null,"selection_policy":null},"id":"265efea6-02a3-48dc-8701-a79cfe1413c5","type":"ColumnDataSource"},{"attributes":{},"id":"c342f708-8fc9-441b-adfb-0df3494d560e","type":"BasicTicker"},{"attributes":{"dimension":1,"plot":{"id":"8939ed4b-ea10-41e3-a20c-b37cbe1209a2","subtype":"Figure","type":"Plot"},"ticker":{"id":"c342f708-8fc9-441b-adfb-0df3494d560e","type":"BasicTicker"}},"id":"4dcf4d13-091d-48bc-a2ee-f8c13853e865","type":"Grid"},{"attributes":{"bottom_units":"screen","fill_alpha":{"value":0.5},"fill_color":{"value":"lightgrey"},"left_units":"screen","level":"overlay","line_alpha":{"value":1.0},"line_color":{"value":"black"},"line_dash":[4,4],"line_width":{"value":2},"plot":null,"render_mode":"css","right_units":"screen","top_units":"screen"},"id":"4232321c-0bd8-44c0-9534-86250766faf8","type":"BoxAnnotation"},{"attributes":{},"id":"1d0a4b09-edc5-4fbb-9d69-efb6a7340323","type":"BasicTickFormatter"}],"root_ids":["8939ed4b-ea10-41e3-a20c-b37cbe1209a2"]},"title":"Bokeh Application","version":"0.12.15"}}';
                  var render_items = [{"docid":"c79b14f6-fb9d-41f6-ad2c-19eca539532e","elementid":"6181baa2-189d-4f05-a8cd-2adc9a039595","modelid":"8939ed4b-ea10-41e3-a20c-b37cbe1209a2"}];
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