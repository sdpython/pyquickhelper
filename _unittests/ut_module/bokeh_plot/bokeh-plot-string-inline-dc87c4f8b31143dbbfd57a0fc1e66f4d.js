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
      };var element = document.getElementById("6c58a158-5dfe-44a6-8701-42d3ec804686");
      if (element == null) {
        console.log("Bokeh: ERROR: autoload.js configured with elementid '6c58a158-5dfe-44a6-8701-42d3ec804686' but no matching script tag was found. ")
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
                    
                  var docs_json = '{"c4a16261-1b62-42f8-9305-81f7369d9cde":{"roots":{"references":[{"attributes":{"fill_color":{"value":"white"},"line_color":{"value":"#1f77b4"},"size":{"units":"screen","value":10},"x":{"field":"x"},"y":{"field":"y"}},"id":"e9b0b99f-c344-4116-a7b6-2d5665c2c78f","type":"Circle"},{"attributes":{"below":[{"id":"70dd02ee-c36c-4187-8c24-9ac59b689566","type":"LinearAxis"}],"left":[{"id":"eb5bf18f-0e06-4fc3-ae97-4798af0e442c","type":"LinearAxis"}],"plot_height":300,"plot_width":300,"renderers":[{"id":"70dd02ee-c36c-4187-8c24-9ac59b689566","type":"LinearAxis"},{"id":"a10804d0-369e-4b2d-95da-b8a0ef20f10f","type":"Grid"},{"id":"eb5bf18f-0e06-4fc3-ae97-4798af0e442c","type":"LinearAxis"},{"id":"abc5f6de-cffe-412b-9ab9-91a2a7bf612d","type":"Grid"},{"id":"e026acf4-c2b4-4597-b527-8fd86295e97a","type":"BoxAnnotation"},{"id":"083e65d9-6cff-4864-ad19-a6b2f8f695ac","type":"GlyphRenderer"},{"id":"463e3d3c-47cc-4aa5-88b7-838c67ed2826","type":"GlyphRenderer"}],"title":{"id":"51483008-8d17-42c8-be90-2f42436e8eba","type":"Title"},"toolbar":{"id":"ea30e2fa-99b2-4641-90d9-11cd6697724e","type":"Toolbar"},"x_range":{"id":"4ebdd585-5945-4b20-b70f-aa800439c6ff","type":"DataRange1d"},"x_scale":{"id":"6a22c5a4-4165-4cb7-b07e-4fea705aad58","type":"LinearScale"},"y_range":{"id":"11d1f271-7224-4cba-ba26-2fb61c7240b7","type":"DataRange1d"},"y_scale":{"id":"7606931a-61ed-4a0c-b780-a0ea5b35fc7c","type":"LinearScale"}},"id":"48023224-210c-4f8d-a41f-389860bffdfa","subtype":"Figure","type":"Plot"},{"attributes":{"source":{"id":"a25629cb-c9c6-4ad5-82e8-10ceacfbdd02","type":"ColumnDataSource"}},"id":"9ae50c7b-3842-414f-9f33-650e366e1ed4","type":"CDSView"},{"attributes":{"data_source":{"id":"a25629cb-c9c6-4ad5-82e8-10ceacfbdd02","type":"ColumnDataSource"},"glyph":{"id":"e3413cc3-ab05-4320-8ce4-6bb25f94840a","type":"Line"},"hover_glyph":null,"muted_glyph":null,"nonselection_glyph":{"id":"ced4d661-473a-4fc2-81c5-ea5488b317fa","type":"Line"},"selection_glyph":null,"view":{"id":"9ae50c7b-3842-414f-9f33-650e366e1ed4","type":"CDSView"}},"id":"083e65d9-6cff-4864-ad19-a6b2f8f695ac","type":"GlyphRenderer"},{"attributes":{"bottom_units":"screen","fill_alpha":{"value":0.5},"fill_color":{"value":"lightgrey"},"left_units":"screen","level":"overlay","line_alpha":{"value":1.0},"line_color":{"value":"black"},"line_dash":[4,4],"line_width":{"value":2},"plot":null,"render_mode":"css","right_units":"screen","top_units":"screen"},"id":"e026acf4-c2b4-4597-b527-8fd86295e97a","type":"BoxAnnotation"},{"attributes":{},"id":"c5fac3f7-227f-4ffa-aef8-6b9d897d91fd","type":"PanTool"},{"attributes":{},"id":"02aeea81-e79d-4149-9e21-251079d45d48","type":"WheelZoomTool"},{"attributes":{"overlay":{"id":"e026acf4-c2b4-4597-b527-8fd86295e97a","type":"BoxAnnotation"}},"id":"e5f24b79-6505-4b7f-9d46-a1effc68f684","type":"BoxZoomTool"},{"attributes":{},"id":"c6ba75bc-be60-493c-8e17-3ec5890972c8","type":"SaveTool"},{"attributes":{"line_color":"#1f77b4","line_width":2,"x":{"field":"x"},"y":{"field":"y"}},"id":"e3413cc3-ab05-4320-8ce4-6bb25f94840a","type":"Line"},{"attributes":{},"id":"f0820aa1-5e31-4241-acd0-6220630aaa49","type":"ResetTool"},{"attributes":{"plot":null,"text":"example_bokeh"},"id":"51483008-8d17-42c8-be90-2f42436e8eba","type":"Title"},{"attributes":{},"id":"a837c389-9a60-423f-9b13-e0789990378c","type":"HelpTool"},{"attributes":{"active_drag":"auto","active_inspect":"auto","active_scroll":"auto","active_tap":"auto","tools":[{"id":"c5fac3f7-227f-4ffa-aef8-6b9d897d91fd","type":"PanTool"},{"id":"02aeea81-e79d-4149-9e21-251079d45d48","type":"WheelZoomTool"},{"id":"e5f24b79-6505-4b7f-9d46-a1effc68f684","type":"BoxZoomTool"},{"id":"c6ba75bc-be60-493c-8e17-3ec5890972c8","type":"SaveTool"},{"id":"f0820aa1-5e31-4241-acd0-6220630aaa49","type":"ResetTool"},{"id":"a837c389-9a60-423f-9b13-e0789990378c","type":"HelpTool"}]},"id":"ea30e2fa-99b2-4641-90d9-11cd6697724e","type":"Toolbar"},{"attributes":{},"id":"be035f90-ba87-42ba-bf6f-eb0f510b81b9","type":"BasicTickFormatter"},{"attributes":{"callback":null},"id":"4ebdd585-5945-4b20-b70f-aa800439c6ff","type":"DataRange1d"},{"attributes":{"data_source":{"id":"fa7654a9-3250-48d9-93ef-184ccc0cea45","type":"ColumnDataSource"},"glyph":{"id":"e9b0b99f-c344-4116-a7b6-2d5665c2c78f","type":"Circle"},"hover_glyph":null,"muted_glyph":null,"nonselection_glyph":{"id":"5e5f06e2-24a6-4847-bca9-7ed5e628cb07","type":"Circle"},"selection_glyph":null,"view":{"id":"66b88119-7f0a-4c74-b41c-60a2586d46fb","type":"CDSView"}},"id":"463e3d3c-47cc-4aa5-88b7-838c67ed2826","type":"GlyphRenderer"},{"attributes":{"callback":null,"column_names":["x","y"],"data":{"x":[1,2,3,4,5],"y":[6,7,6,4,5]},"selected":null,"selection_policy":null},"id":"fa7654a9-3250-48d9-93ef-184ccc0cea45","type":"ColumnDataSource"},{"attributes":{},"id":"59e5dac9-24e6-4429-b296-e956bc427190","type":"BasicTickFormatter"},{"attributes":{"fill_alpha":{"value":0.1},"fill_color":{"value":"#1f77b4"},"line_alpha":{"value":0.1},"line_color":{"value":"#1f77b4"},"size":{"units":"screen","value":10},"x":{"field":"x"},"y":{"field":"y"}},"id":"5e5f06e2-24a6-4847-bca9-7ed5e628cb07","type":"Circle"},{"attributes":{"formatter":{"id":"be035f90-ba87-42ba-bf6f-eb0f510b81b9","type":"BasicTickFormatter"},"plot":{"id":"48023224-210c-4f8d-a41f-389860bffdfa","subtype":"Figure","type":"Plot"},"ticker":{"id":"cbe58c35-6df5-4e18-aedf-4b2de5a383d6","type":"BasicTicker"}},"id":"eb5bf18f-0e06-4fc3-ae97-4798af0e442c","type":"LinearAxis"},{"attributes":{"source":{"id":"fa7654a9-3250-48d9-93ef-184ccc0cea45","type":"ColumnDataSource"}},"id":"66b88119-7f0a-4c74-b41c-60a2586d46fb","type":"CDSView"},{"attributes":{"callback":null},"id":"11d1f271-7224-4cba-ba26-2fb61c7240b7","type":"DataRange1d"},{"attributes":{"line_alpha":0.1,"line_color":"#1f77b4","line_width":2,"x":{"field":"x"},"y":{"field":"y"}},"id":"ced4d661-473a-4fc2-81c5-ea5488b317fa","type":"Line"},{"attributes":{},"id":"6a22c5a4-4165-4cb7-b07e-4fea705aad58","type":"LinearScale"},{"attributes":{},"id":"7606931a-61ed-4a0c-b780-a0ea5b35fc7c","type":"LinearScale"},{"attributes":{"callback":null,"column_names":["x","y"],"data":{"x":[1,2,3,4,5],"y":[6,7,6,4,5]},"selected":null,"selection_policy":null},"id":"a25629cb-c9c6-4ad5-82e8-10ceacfbdd02","type":"ColumnDataSource"},{"attributes":{},"id":"cbe58c35-6df5-4e18-aedf-4b2de5a383d6","type":"BasicTicker"},{"attributes":{"formatter":{"id":"59e5dac9-24e6-4429-b296-e956bc427190","type":"BasicTickFormatter"},"plot":{"id":"48023224-210c-4f8d-a41f-389860bffdfa","subtype":"Figure","type":"Plot"},"ticker":{"id":"e57c4db9-b10e-4acd-b5a9-914cdf48e7f0","type":"BasicTicker"}},"id":"70dd02ee-c36c-4187-8c24-9ac59b689566","type":"LinearAxis"},{"attributes":{},"id":"e57c4db9-b10e-4acd-b5a9-914cdf48e7f0","type":"BasicTicker"},{"attributes":{"plot":{"id":"48023224-210c-4f8d-a41f-389860bffdfa","subtype":"Figure","type":"Plot"},"ticker":{"id":"e57c4db9-b10e-4acd-b5a9-914cdf48e7f0","type":"BasicTicker"}},"id":"a10804d0-369e-4b2d-95da-b8a0ef20f10f","type":"Grid"},{"attributes":{"dimension":1,"plot":{"id":"48023224-210c-4f8d-a41f-389860bffdfa","subtype":"Figure","type":"Plot"},"ticker":{"id":"cbe58c35-6df5-4e18-aedf-4b2de5a383d6","type":"BasicTicker"}},"id":"abc5f6de-cffe-412b-9ab9-91a2a7bf612d","type":"Grid"}],"root_ids":["48023224-210c-4f8d-a41f-389860bffdfa"]},"title":"Bokeh Application","version":"0.12.15"}}';
                  var render_items = [{"docid":"c4a16261-1b62-42f8-9305-81f7369d9cde","elementid":"6c58a158-5dfe-44a6-8701-42d3ec804686","modelid":"48023224-210c-4f8d-a41f-389860bffdfa"}];
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