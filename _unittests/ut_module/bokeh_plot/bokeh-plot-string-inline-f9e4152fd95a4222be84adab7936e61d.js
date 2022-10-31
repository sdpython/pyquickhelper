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
      };var element = document.getElementById("26ea7797-69c7-455d-a08b-a5a104821274");
      if (element == null) {
        console.log("Bokeh: ERROR: autoload.js configured with elementid '26ea7797-69c7-455d-a08b-a5a104821274' but no matching script tag was found. ")
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
                    
                  var docs_json = '{"e40c6e46-512c-46e2-a795-cf6396ed2b92":{"roots":{"references":[{"attributes":{"below":[{"id":"2e000fef-17e1-4076-aaf7-96f430591179","type":"LinearAxis"}],"left":[{"id":"c1840aac-5c01-43c4-a9e5-763752a0ca48","type":"LinearAxis"}],"plot_height":300,"plot_width":300,"renderers":[{"id":"2e000fef-17e1-4076-aaf7-96f430591179","type":"LinearAxis"},{"id":"e570d140-0f63-4337-9824-8871e4684e26","type":"Grid"},{"id":"c1840aac-5c01-43c4-a9e5-763752a0ca48","type":"LinearAxis"},{"id":"60333206-a5a1-4040-931c-e9035e750328","type":"Grid"},{"id":"f07fc7f8-9041-4c87-9d37-d20d4786f11b","type":"BoxAnnotation"},{"id":"3cf4c276-b221-4980-a705-bd5695b854e2","type":"GlyphRenderer"},{"id":"3b90b6ec-d60e-4cd1-a890-21257fc2b11d","type":"GlyphRenderer"}],"title":{"id":"653cc1d8-97f5-486b-99bc-f43dce2614d1","type":"Title"},"toolbar":{"id":"475a0532-bba9-4e27-9b9c-be54838dac42","type":"Toolbar"},"x_range":{"id":"0452c4fc-522a-4eb1-8b4a-7bb0d9ff489f","type":"DataRange1d"},"x_scale":{"id":"87c18d08-2e57-46ab-b09e-76a1821e4756","type":"LinearScale"},"y_range":{"id":"3fae3e35-2fb9-43c2-886d-7b5115a12b8c","type":"DataRange1d"},"y_scale":{"id":"71bfa455-b6f3-40fe-864c-14ec31105581","type":"LinearScale"}},"id":"9117148e-8325-465a-ad3a-708421cc6ab6","subtype":"Figure","type":"Plot"},{"attributes":{},"id":"8a325ed2-6df8-459a-9aad-180ab0591475","type":"BasicTickFormatter"},{"attributes":{"dimension":1,"plot":{"id":"9117148e-8325-465a-ad3a-708421cc6ab6","subtype":"Figure","type":"Plot"},"ticker":{"id":"4cde73d9-0cdd-4a04-a805-990749bdc3fa","type":"BasicTicker"}},"id":"60333206-a5a1-4040-931c-e9035e750328","type":"Grid"},{"attributes":{"data_source":{"id":"8d6dbc39-66ab-4f57-a096-4b6f97c8048f","type":"ColumnDataSource"},"glyph":{"id":"8716bdab-609b-47d0-a94f-c7d4102990dd","type":"Line"},"hover_glyph":null,"muted_glyph":null,"nonselection_glyph":{"id":"a083e0fd-e654-4d01-b362-01c876151101","type":"Line"},"selection_glyph":null,"view":{"id":"b5cc02db-a81d-4eb0-abb8-443ad97ff117","type":"CDSView"}},"id":"3cf4c276-b221-4980-a705-bd5695b854e2","type":"GlyphRenderer"},{"attributes":{"bottom_units":"screen","fill_alpha":{"value":0.5},"fill_color":{"value":"lightgrey"},"left_units":"screen","level":"overlay","line_alpha":{"value":1.0},"line_color":{"value":"black"},"line_dash":[4,4],"line_width":{"value":2},"plot":null,"render_mode":"css","right_units":"screen","top_units":"screen"},"id":"f07fc7f8-9041-4c87-9d37-d20d4786f11b","type":"BoxAnnotation"},{"attributes":{"line_color":"#1f77b4","line_width":2,"x":{"field":"x"},"y":{"field":"y"}},"id":"8716bdab-609b-47d0-a94f-c7d4102990dd","type":"Line"},{"attributes":{"line_alpha":0.1,"line_color":"#1f77b4","line_width":2,"x":{"field":"x"},"y":{"field":"y"}},"id":"a083e0fd-e654-4d01-b362-01c876151101","type":"Line"},{"attributes":{},"id":"35702ddf-fcbd-4319-89e9-39971080bd28","type":"PanTool"},{"attributes":{"callback":null,"column_names":["x","y"],"data":{"x":[1,2,3,4,5],"y":[6,7,6,4,5]},"selected":null,"selection_policy":null},"id":"8d6dbc39-66ab-4f57-a096-4b6f97c8048f","type":"ColumnDataSource"},{"attributes":{},"id":"24922f87-5fa0-4f43-9545-0898442f073b","type":"WheelZoomTool"},{"attributes":{"callback":null},"id":"0452c4fc-522a-4eb1-8b4a-7bb0d9ff489f","type":"DataRange1d"},{"attributes":{},"id":"87c18d08-2e57-46ab-b09e-76a1821e4756","type":"LinearScale"},{"attributes":{"overlay":{"id":"f07fc7f8-9041-4c87-9d37-d20d4786f11b","type":"BoxAnnotation"}},"id":"d40dd068-0e42-4737-b553-a74977a37f17","type":"BoxZoomTool"},{"attributes":{},"id":"50b3bad7-5e75-4d4c-919a-bc8096dff622","type":"SaveTool"},{"attributes":{},"id":"1a16b09c-8c79-4377-889b-1cc18e7842dc","type":"ResetTool"},{"attributes":{"plot":null,"text":"example_bokeh"},"id":"653cc1d8-97f5-486b-99bc-f43dce2614d1","type":"Title"},{"attributes":{},"id":"429613a5-f7c1-446a-96d8-831f7bfe6c79","type":"HelpTool"},{"attributes":{},"id":"d0ee0b03-bb51-4711-980e-cd8a7f57c79f","type":"BasicTickFormatter"},{"attributes":{"callback":null},"id":"3fae3e35-2fb9-43c2-886d-7b5115a12b8c","type":"DataRange1d"},{"attributes":{"fill_alpha":{"value":0.1},"fill_color":{"value":"#1f77b4"},"line_alpha":{"value":0.1},"line_color":{"value":"#1f77b4"},"size":{"units":"screen","value":10},"x":{"field":"x"},"y":{"field":"y"}},"id":"50bea5ae-3fbc-47f6-8e14-b87727d4351d","type":"Circle"},{"attributes":{},"id":"71bfa455-b6f3-40fe-864c-14ec31105581","type":"LinearScale"},{"attributes":{"data_source":{"id":"eb29627f-a05d-455c-a6f2-cd7ea466d68c","type":"ColumnDataSource"},"glyph":{"id":"f2f71a6f-4109-4c8c-8bf6-0c63c67af584","type":"Circle"},"hover_glyph":null,"muted_glyph":null,"nonselection_glyph":{"id":"50bea5ae-3fbc-47f6-8e14-b87727d4351d","type":"Circle"},"selection_glyph":null,"view":{"id":"512d041e-cd64-4bf5-a1e6-9182664b4b42","type":"CDSView"}},"id":"3b90b6ec-d60e-4cd1-a890-21257fc2b11d","type":"GlyphRenderer"},{"attributes":{"callback":null,"column_names":["x","y"],"data":{"x":[1,2,3,4,5],"y":[6,7,6,4,5]},"selected":null,"selection_policy":null},"id":"eb29627f-a05d-455c-a6f2-cd7ea466d68c","type":"ColumnDataSource"},{"attributes":{"source":{"id":"8d6dbc39-66ab-4f57-a096-4b6f97c8048f","type":"ColumnDataSource"}},"id":"b5cc02db-a81d-4eb0-abb8-443ad97ff117","type":"CDSView"},{"attributes":{"fill_color":{"value":"white"},"line_color":{"value":"#1f77b4"},"size":{"units":"screen","value":10},"x":{"field":"x"},"y":{"field":"y"}},"id":"f2f71a6f-4109-4c8c-8bf6-0c63c67af584","type":"Circle"},{"attributes":{"source":{"id":"eb29627f-a05d-455c-a6f2-cd7ea466d68c","type":"ColumnDataSource"}},"id":"512d041e-cd64-4bf5-a1e6-9182664b4b42","type":"CDSView"},{"attributes":{"plot":{"id":"9117148e-8325-465a-ad3a-708421cc6ab6","subtype":"Figure","type":"Plot"},"ticker":{"id":"ec4523c0-05f5-4b7c-ac5f-367e6f8e81fe","type":"BasicTicker"}},"id":"e570d140-0f63-4337-9824-8871e4684e26","type":"Grid"},{"attributes":{"active_drag":"auto","active_inspect":"auto","active_scroll":"auto","active_tap":"auto","tools":[{"id":"35702ddf-fcbd-4319-89e9-39971080bd28","type":"PanTool"},{"id":"24922f87-5fa0-4f43-9545-0898442f073b","type":"WheelZoomTool"},{"id":"d40dd068-0e42-4737-b553-a74977a37f17","type":"BoxZoomTool"},{"id":"50b3bad7-5e75-4d4c-919a-bc8096dff622","type":"SaveTool"},{"id":"1a16b09c-8c79-4377-889b-1cc18e7842dc","type":"ResetTool"},{"id":"429613a5-f7c1-446a-96d8-831f7bfe6c79","type":"HelpTool"}]},"id":"475a0532-bba9-4e27-9b9c-be54838dac42","type":"Toolbar"},{"attributes":{"formatter":{"id":"8a325ed2-6df8-459a-9aad-180ab0591475","type":"BasicTickFormatter"},"plot":{"id":"9117148e-8325-465a-ad3a-708421cc6ab6","subtype":"Figure","type":"Plot"},"ticker":{"id":"4cde73d9-0cdd-4a04-a805-990749bdc3fa","type":"BasicTicker"}},"id":"c1840aac-5c01-43c4-a9e5-763752a0ca48","type":"LinearAxis"},{"attributes":{"formatter":{"id":"d0ee0b03-bb51-4711-980e-cd8a7f57c79f","type":"BasicTickFormatter"},"plot":{"id":"9117148e-8325-465a-ad3a-708421cc6ab6","subtype":"Figure","type":"Plot"},"ticker":{"id":"ec4523c0-05f5-4b7c-ac5f-367e6f8e81fe","type":"BasicTicker"}},"id":"2e000fef-17e1-4076-aaf7-96f430591179","type":"LinearAxis"},{"attributes":{},"id":"4cde73d9-0cdd-4a04-a805-990749bdc3fa","type":"BasicTicker"},{"attributes":{},"id":"ec4523c0-05f5-4b7c-ac5f-367e6f8e81fe","type":"BasicTicker"}],"root_ids":["9117148e-8325-465a-ad3a-708421cc6ab6"]},"title":"Bokeh Application","version":"0.12.15"}}';
                  var render_items = [{"docid":"e40c6e46-512c-46e2-a795-cf6396ed2b92","elementid":"26ea7797-69c7-455d-a08b-a5a104821274","modelid":"9117148e-8325-465a-ad3a-708421cc6ab6"}];
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