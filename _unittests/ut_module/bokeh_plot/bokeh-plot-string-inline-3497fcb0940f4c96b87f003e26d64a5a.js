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
      };var element = document.getElementById("a054e6c3-cdd6-4413-9f23-dc3afd0139fd");
      if (element == null) {
        console.log("Bokeh: ERROR: autoload.js configured with elementid 'a054e6c3-cdd6-4413-9f23-dc3afd0139fd' but no matching script tag was found. ")
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
                    
                  var docs_json = '{"3be9d434-9fad-43fe-826d-1b3d61a09648":{"roots":{"references":[{"attributes":{"data_source":{"id":"113bae76-9ede-4090-a8bd-cc134d75765b","type":"ColumnDataSource"},"glyph":{"id":"5671ff5a-0852-4c91-a20d-19a8fbb64406","type":"Line"},"hover_glyph":null,"muted_glyph":null,"nonselection_glyph":{"id":"35130f27-1632-48ef-b5dd-ae7a445941e5","type":"Line"},"selection_glyph":null,"view":{"id":"a529391f-8b54-44ed-8e38-b2adbb0357c5","type":"CDSView"}},"id":"0d23fe70-9e02-4408-ae6e-f718e1569702","type":"GlyphRenderer"},{"attributes":{},"id":"56dc69b4-53fd-4e62-b81f-ac10af3cc2ac","type":"PanTool"},{"attributes":{"line_color":"#1f77b4","line_width":2,"x":{"field":"x"},"y":{"field":"y"}},"id":"5671ff5a-0852-4c91-a20d-19a8fbb64406","type":"Line"},{"attributes":{},"id":"30ea9032-d69c-408c-a5fc-baae63f9c721","type":"WheelZoomTool"},{"attributes":{"line_alpha":0.1,"line_color":"#1f77b4","line_width":2,"x":{"field":"x"},"y":{"field":"y"}},"id":"35130f27-1632-48ef-b5dd-ae7a445941e5","type":"Line"},{"attributes":{"overlay":{"id":"f8323d80-d627-4803-be6c-b0f89889e38e","type":"BoxAnnotation"}},"id":"7e8702f7-ff4e-42d5-9b30-b77f833be366","type":"BoxZoomTool"},{"attributes":{},"id":"40017264-e065-4952-a9ad-27ac16a261f5","type":"SaveTool"},{"attributes":{},"id":"d423282c-f9ae-4543-807d-b069ad713692","type":"LinearScale"},{"attributes":{},"id":"b8e4fd68-29c9-4fb8-866c-7b68cd805646","type":"ResetTool"},{"attributes":{},"id":"2a829ecb-fe22-494b-8b3a-d9d67b3c76dc","type":"HelpTool"},{"attributes":{"callback":null},"id":"c5fcdd42-dd8b-4e8a-9280-dc83069d199c","type":"DataRange1d"},{"attributes":{},"id":"fb31b4eb-2c2e-4a58-bc07-322afd519568","type":"BasicTickFormatter"},{"attributes":{"source":{"id":"1eb4b1e0-f103-4e8b-8082-43e25431e501","type":"ColumnDataSource"}},"id":"031c8f60-50c3-4c52-b17d-a40e6bed5091","type":"CDSView"},{"attributes":{"fill_alpha":{"value":0.1},"fill_color":{"value":"#1f77b4"},"line_alpha":{"value":0.1},"line_color":{"value":"#1f77b4"},"size":{"units":"screen","value":10},"x":{"field":"x"},"y":{"field":"y"}},"id":"12f3320d-4775-4763-a92c-03efe26a018c","type":"Circle"},{"attributes":{"fill_color":{"value":"white"},"line_color":{"value":"#1f77b4"},"size":{"units":"screen","value":10},"x":{"field":"x"},"y":{"field":"y"}},"id":"4400a852-4c36-4488-b800-eb153fe3a98f","type":"Circle"},{"attributes":{"data_source":{"id":"1eb4b1e0-f103-4e8b-8082-43e25431e501","type":"ColumnDataSource"},"glyph":{"id":"4400a852-4c36-4488-b800-eb153fe3a98f","type":"Circle"},"hover_glyph":null,"muted_glyph":null,"nonselection_glyph":{"id":"12f3320d-4775-4763-a92c-03efe26a018c","type":"Circle"},"selection_glyph":null,"view":{"id":"031c8f60-50c3-4c52-b17d-a40e6bed5091","type":"CDSView"}},"id":"5028b356-e555-4d0a-bf6e-8b4cdb2dcad1","type":"GlyphRenderer"},{"attributes":{},"id":"55891c33-bd97-4b80-88dc-3c4bd1eb99ac","type":"BasicTickFormatter"},{"attributes":{"source":{"id":"113bae76-9ede-4090-a8bd-cc134d75765b","type":"ColumnDataSource"}},"id":"a529391f-8b54-44ed-8e38-b2adbb0357c5","type":"CDSView"},{"attributes":{"active_drag":"auto","active_inspect":"auto","active_scroll":"auto","active_tap":"auto","tools":[{"id":"56dc69b4-53fd-4e62-b81f-ac10af3cc2ac","type":"PanTool"},{"id":"30ea9032-d69c-408c-a5fc-baae63f9c721","type":"WheelZoomTool"},{"id":"7e8702f7-ff4e-42d5-9b30-b77f833be366","type":"BoxZoomTool"},{"id":"40017264-e065-4952-a9ad-27ac16a261f5","type":"SaveTool"},{"id":"b8e4fd68-29c9-4fb8-866c-7b68cd805646","type":"ResetTool"},{"id":"2a829ecb-fe22-494b-8b3a-d9d67b3c76dc","type":"HelpTool"}]},"id":"4022b7da-1e3d-4407-b7b8-83127a7cc269","type":"Toolbar"},{"attributes":{"plot":null,"text":"example_bokeh"},"id":"2e3a1c35-8a42-4de1-9f00-8c9ce156b1fc","type":"Title"},{"attributes":{},"id":"3892b075-efb2-45b0-9900-3b80be020624","type":"LinearScale"},{"attributes":{"formatter":{"id":"55891c33-bd97-4b80-88dc-3c4bd1eb99ac","type":"BasicTickFormatter"},"plot":{"id":"4d5b0225-7dd9-4f30-8bd0-a0fceb3d1f3b","subtype":"Figure","type":"Plot"},"ticker":{"id":"e872dc6f-9e27-43c2-95d5-8e47b645572f","type":"BasicTicker"}},"id":"e849dd0e-8d11-4c51-ad56-5f8b43b5a40d","type":"LinearAxis"},{"attributes":{"callback":null,"column_names":["x","y"],"data":{"x":[1,2,3,4,5],"y":[6,7,6,4,5]},"selected":null,"selection_policy":null},"id":"113bae76-9ede-4090-a8bd-cc134d75765b","type":"ColumnDataSource"},{"attributes":{"below":[{"id":"375c6f41-ac41-4f27-9f7b-76e2f70738ef","type":"LinearAxis"}],"left":[{"id":"e849dd0e-8d11-4c51-ad56-5f8b43b5a40d","type":"LinearAxis"}],"plot_height":300,"plot_width":300,"renderers":[{"id":"375c6f41-ac41-4f27-9f7b-76e2f70738ef","type":"LinearAxis"},{"id":"80a2c7ec-1413-45a2-a67e-b695bdefcb87","type":"Grid"},{"id":"e849dd0e-8d11-4c51-ad56-5f8b43b5a40d","type":"LinearAxis"},{"id":"e8c4a7cf-4ce3-4dba-88da-aadbf47a4e94","type":"Grid"},{"id":"f8323d80-d627-4803-be6c-b0f89889e38e","type":"BoxAnnotation"},{"id":"0d23fe70-9e02-4408-ae6e-f718e1569702","type":"GlyphRenderer"},{"id":"5028b356-e555-4d0a-bf6e-8b4cdb2dcad1","type":"GlyphRenderer"}],"title":{"id":"2e3a1c35-8a42-4de1-9f00-8c9ce156b1fc","type":"Title"},"toolbar":{"id":"4022b7da-1e3d-4407-b7b8-83127a7cc269","type":"Toolbar"},"x_range":{"id":"3600d641-f820-4e02-be08-3d6913c5c3a2","type":"DataRange1d"},"x_scale":{"id":"d423282c-f9ae-4543-807d-b069ad713692","type":"LinearScale"},"y_range":{"id":"c5fcdd42-dd8b-4e8a-9280-dc83069d199c","type":"DataRange1d"},"y_scale":{"id":"3892b075-efb2-45b0-9900-3b80be020624","type":"LinearScale"}},"id":"4d5b0225-7dd9-4f30-8bd0-a0fceb3d1f3b","subtype":"Figure","type":"Plot"},{"attributes":{"plot":{"id":"4d5b0225-7dd9-4f30-8bd0-a0fceb3d1f3b","subtype":"Figure","type":"Plot"},"ticker":{"id":"57d1778f-e08d-48a7-a062-ec054c7ca032","type":"BasicTicker"}},"id":"80a2c7ec-1413-45a2-a67e-b695bdefcb87","type":"Grid"},{"attributes":{"callback":null},"id":"3600d641-f820-4e02-be08-3d6913c5c3a2","type":"DataRange1d"},{"attributes":{"formatter":{"id":"fb31b4eb-2c2e-4a58-bc07-322afd519568","type":"BasicTickFormatter"},"plot":{"id":"4d5b0225-7dd9-4f30-8bd0-a0fceb3d1f3b","subtype":"Figure","type":"Plot"},"ticker":{"id":"57d1778f-e08d-48a7-a062-ec054c7ca032","type":"BasicTicker"}},"id":"375c6f41-ac41-4f27-9f7b-76e2f70738ef","type":"LinearAxis"},{"attributes":{},"id":"57d1778f-e08d-48a7-a062-ec054c7ca032","type":"BasicTicker"},{"attributes":{},"id":"e872dc6f-9e27-43c2-95d5-8e47b645572f","type":"BasicTicker"},{"attributes":{"dimension":1,"plot":{"id":"4d5b0225-7dd9-4f30-8bd0-a0fceb3d1f3b","subtype":"Figure","type":"Plot"},"ticker":{"id":"e872dc6f-9e27-43c2-95d5-8e47b645572f","type":"BasicTicker"}},"id":"e8c4a7cf-4ce3-4dba-88da-aadbf47a4e94","type":"Grid"},{"attributes":{"bottom_units":"screen","fill_alpha":{"value":0.5},"fill_color":{"value":"lightgrey"},"left_units":"screen","level":"overlay","line_alpha":{"value":1.0},"line_color":{"value":"black"},"line_dash":[4,4],"line_width":{"value":2},"plot":null,"render_mode":"css","right_units":"screen","top_units":"screen"},"id":"f8323d80-d627-4803-be6c-b0f89889e38e","type":"BoxAnnotation"},{"attributes":{"callback":null,"column_names":["x","y"],"data":{"x":[1,2,3,4,5],"y":[6,7,6,4,5]},"selected":null,"selection_policy":null},"id":"1eb4b1e0-f103-4e8b-8082-43e25431e501","type":"ColumnDataSource"}],"root_ids":["4d5b0225-7dd9-4f30-8bd0-a0fceb3d1f3b"]},"title":"Bokeh Application","version":"0.12.15"}}';
                  var render_items = [{"docid":"3be9d434-9fad-43fe-826d-1b3d61a09648","elementid":"a054e6c3-cdd6-4413-9f23-dc3afd0139fd","modelid":"4d5b0225-7dd9-4f30-8bd0-a0fceb3d1f3b"}];
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