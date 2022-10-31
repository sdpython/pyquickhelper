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
      };var element = document.getElementById("8b35dc98-3226-4e99-aebf-621e848a5f63");
      if (element == null) {
        console.log("Bokeh: ERROR: autoload.js configured with elementid '8b35dc98-3226-4e99-aebf-621e848a5f63' but no matching script tag was found. ")
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
                    
                  var docs_json = '{"124b019c-6f3b-4679-a012-60657555d6ed":{"roots":{"references":[{"attributes":{"line_color":"#1f77b4","line_width":2,"x":{"field":"x"},"y":{"field":"y"}},"id":"1f76c492-1f48-4598-95dd-abe0641e65b2","type":"Line"},{"attributes":{},"id":"2cd60a8f-43bd-4efd-919c-751b12b4f1b1","type":"PanTool"},{"attributes":{"data_source":{"id":"0c38cc8b-1ef0-46d6-af38-375fab6e3b4f","type":"ColumnDataSource"},"glyph":{"id":"1f76c492-1f48-4598-95dd-abe0641e65b2","type":"Line"},"hover_glyph":null,"muted_glyph":null,"nonselection_glyph":{"id":"f3b5f460-303e-4ea2-83a4-00fbc5074273","type":"Line"},"selection_glyph":null,"view":{"id":"e10a5fae-8a97-49fc-83c5-2229d25395b4","type":"CDSView"}},"id":"427b5a77-d7b7-46d8-bb84-d3fb8b51d334","type":"GlyphRenderer"},{"attributes":{"fill_color":{"value":"white"},"line_color":{"value":"#1f77b4"},"size":{"units":"screen","value":10},"x":{"field":"x"},"y":{"field":"y"}},"id":"ef3a85b2-c4e4-4f2d-b649-1d9473900098","type":"Circle"},{"attributes":{"callback":null},"id":"ad60c94c-c54f-4757-b3ba-779481fe47c2","type":"DataRange1d"},{"attributes":{},"id":"1c12360a-1ed8-4eec-9169-0a09036e9fd7","type":"WheelZoomTool"},{"attributes":{"line_alpha":0.1,"line_color":"#1f77b4","line_width":2,"x":{"field":"x"},"y":{"field":"y"}},"id":"f3b5f460-303e-4ea2-83a4-00fbc5074273","type":"Line"},{"attributes":{"overlay":{"id":"13df976d-9fc1-4b45-b85b-ba0f2cb14dad","type":"BoxAnnotation"}},"id":"7c4c3097-4d65-415f-b7d0-adcebeb04099","type":"BoxZoomTool"},{"attributes":{},"id":"d8ac5700-8b74-403e-9519-d9ce7b8b6059","type":"SaveTool"},{"attributes":{},"id":"a857bac0-ccc0-4cb9-b420-57833dc0b3b2","type":"LinearScale"},{"attributes":{},"id":"3c4118eb-99be-4082-9ad2-f3af8830bf36","type":"ResetTool"},{"attributes":{},"id":"644a30ab-997b-4c30-9a46-57f22b310bc9","type":"HelpTool"},{"attributes":{"callback":null},"id":"cc2af270-0deb-4f08-98a2-a7f4f1453e8e","type":"DataRange1d"},{"attributes":{},"id":"43ccee34-12cd-4c84-8e71-818e4664bd3d","type":"BasicTickFormatter"},{"attributes":{"callback":null,"column_names":["x","y"],"data":{"x":[1,2,3,4,5],"y":[6,7,6,4,5]},"selected":null,"selection_policy":null},"id":"159edfde-e0c2-415e-bd17-d4a1a344c688","type":"ColumnDataSource"},{"attributes":{"data_source":{"id":"159edfde-e0c2-415e-bd17-d4a1a344c688","type":"ColumnDataSource"},"glyph":{"id":"ef3a85b2-c4e4-4f2d-b649-1d9473900098","type":"Circle"},"hover_glyph":null,"muted_glyph":null,"nonselection_glyph":{"id":"cc8651ca-fb7c-4ccf-b42f-e0a574a95945","type":"Circle"},"selection_glyph":null,"view":{"id":"46c355ba-5237-4372-b169-0c4d410bf6d7","type":"CDSView"}},"id":"d6696cbe-771c-4820-af61-38bb13a5011e","type":"GlyphRenderer"},{"attributes":{"source":{"id":"159edfde-e0c2-415e-bd17-d4a1a344c688","type":"ColumnDataSource"}},"id":"46c355ba-5237-4372-b169-0c4d410bf6d7","type":"CDSView"},{"attributes":{"source":{"id":"0c38cc8b-1ef0-46d6-af38-375fab6e3b4f","type":"ColumnDataSource"}},"id":"e10a5fae-8a97-49fc-83c5-2229d25395b4","type":"CDSView"},{"attributes":{"plot":null,"text":"example_bokeh"},"id":"5487932e-bdd1-46db-84c2-6b6f70257c3d","type":"Title"},{"attributes":{},"id":"82328003-d414-4434-9c94-b7f549923f1a","type":"LinearScale"},{"attributes":{"formatter":{"id":"43ccee34-12cd-4c84-8e71-818e4664bd3d","type":"BasicTickFormatter"},"plot":{"id":"b181ebef-2772-45c0-a398-2cf9922bd147","subtype":"Figure","type":"Plot"},"ticker":{"id":"ad9d8fdb-2730-4f58-a887-28d6f758cec5","type":"BasicTicker"}},"id":"5a199b40-e6e0-4d0a-bb8f-2acd1a9d4c5d","type":"LinearAxis"},{"attributes":{},"id":"590c2733-7811-49d4-8dbc-c97f34c6fd1f","type":"BasicTickFormatter"},{"attributes":{"below":[{"id":"40830496-032d-4e81-9c1d-5d91155494fa","type":"LinearAxis"}],"left":[{"id":"5a199b40-e6e0-4d0a-bb8f-2acd1a9d4c5d","type":"LinearAxis"}],"plot_height":300,"plot_width":300,"renderers":[{"id":"40830496-032d-4e81-9c1d-5d91155494fa","type":"LinearAxis"},{"id":"a036f29e-748d-4f39-956b-a2ca70fafe97","type":"Grid"},{"id":"5a199b40-e6e0-4d0a-bb8f-2acd1a9d4c5d","type":"LinearAxis"},{"id":"5b32d6b3-d7fd-4480-b73f-0e9ce2d19fe2","type":"Grid"},{"id":"13df976d-9fc1-4b45-b85b-ba0f2cb14dad","type":"BoxAnnotation"},{"id":"427b5a77-d7b7-46d8-bb84-d3fb8b51d334","type":"GlyphRenderer"},{"id":"d6696cbe-771c-4820-af61-38bb13a5011e","type":"GlyphRenderer"}],"title":{"id":"5487932e-bdd1-46db-84c2-6b6f70257c3d","type":"Title"},"toolbar":{"id":"c85455f9-236a-4651-ab31-4cba5cd94048","type":"Toolbar"},"x_range":{"id":"ad60c94c-c54f-4757-b3ba-779481fe47c2","type":"DataRange1d"},"x_scale":{"id":"a857bac0-ccc0-4cb9-b420-57833dc0b3b2","type":"LinearScale"},"y_range":{"id":"cc2af270-0deb-4f08-98a2-a7f4f1453e8e","type":"DataRange1d"},"y_scale":{"id":"82328003-d414-4434-9c94-b7f549923f1a","type":"LinearScale"}},"id":"b181ebef-2772-45c0-a398-2cf9922bd147","subtype":"Figure","type":"Plot"},{"attributes":{"formatter":{"id":"590c2733-7811-49d4-8dbc-c97f34c6fd1f","type":"BasicTickFormatter"},"plot":{"id":"b181ebef-2772-45c0-a398-2cf9922bd147","subtype":"Figure","type":"Plot"},"ticker":{"id":"39055e84-c1c1-4fd6-b7c5-b820e871d8ee","type":"BasicTicker"}},"id":"40830496-032d-4e81-9c1d-5d91155494fa","type":"LinearAxis"},{"attributes":{"callback":null,"column_names":["x","y"],"data":{"x":[1,2,3,4,5],"y":[6,7,6,4,5]},"selected":null,"selection_policy":null},"id":"0c38cc8b-1ef0-46d6-af38-375fab6e3b4f","type":"ColumnDataSource"},{"attributes":{},"id":"39055e84-c1c1-4fd6-b7c5-b820e871d8ee","type":"BasicTicker"},{"attributes":{"plot":{"id":"b181ebef-2772-45c0-a398-2cf9922bd147","subtype":"Figure","type":"Plot"},"ticker":{"id":"39055e84-c1c1-4fd6-b7c5-b820e871d8ee","type":"BasicTicker"}},"id":"a036f29e-748d-4f39-956b-a2ca70fafe97","type":"Grid"},{"attributes":{},"id":"ad9d8fdb-2730-4f58-a887-28d6f758cec5","type":"BasicTicker"},{"attributes":{"dimension":1,"plot":{"id":"b181ebef-2772-45c0-a398-2cf9922bd147","subtype":"Figure","type":"Plot"},"ticker":{"id":"ad9d8fdb-2730-4f58-a887-28d6f758cec5","type":"BasicTicker"}},"id":"5b32d6b3-d7fd-4480-b73f-0e9ce2d19fe2","type":"Grid"},{"attributes":{"active_drag":"auto","active_inspect":"auto","active_scroll":"auto","active_tap":"auto","tools":[{"id":"2cd60a8f-43bd-4efd-919c-751b12b4f1b1","type":"PanTool"},{"id":"1c12360a-1ed8-4eec-9169-0a09036e9fd7","type":"WheelZoomTool"},{"id":"7c4c3097-4d65-415f-b7d0-adcebeb04099","type":"BoxZoomTool"},{"id":"d8ac5700-8b74-403e-9519-d9ce7b8b6059","type":"SaveTool"},{"id":"3c4118eb-99be-4082-9ad2-f3af8830bf36","type":"ResetTool"},{"id":"644a30ab-997b-4c30-9a46-57f22b310bc9","type":"HelpTool"}]},"id":"c85455f9-236a-4651-ab31-4cba5cd94048","type":"Toolbar"},{"attributes":{"bottom_units":"screen","fill_alpha":{"value":0.5},"fill_color":{"value":"lightgrey"},"left_units":"screen","level":"overlay","line_alpha":{"value":1.0},"line_color":{"value":"black"},"line_dash":[4,4],"line_width":{"value":2},"plot":null,"render_mode":"css","right_units":"screen","top_units":"screen"},"id":"13df976d-9fc1-4b45-b85b-ba0f2cb14dad","type":"BoxAnnotation"},{"attributes":{"fill_alpha":{"value":0.1},"fill_color":{"value":"#1f77b4"},"line_alpha":{"value":0.1},"line_color":{"value":"#1f77b4"},"size":{"units":"screen","value":10},"x":{"field":"x"},"y":{"field":"y"}},"id":"cc8651ca-fb7c-4ccf-b42f-e0a574a95945","type":"Circle"}],"root_ids":["b181ebef-2772-45c0-a398-2cf9922bd147"]},"title":"Bokeh Application","version":"0.12.15"}}';
                  var render_items = [{"docid":"124b019c-6f3b-4679-a012-60657555d6ed","elementid":"8b35dc98-3226-4e99-aebf-621e848a5f63","modelid":"b181ebef-2772-45c0-a398-2cf9922bd147"}];
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