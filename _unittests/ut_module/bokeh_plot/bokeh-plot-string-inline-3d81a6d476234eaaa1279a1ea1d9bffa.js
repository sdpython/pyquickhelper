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
      };var element = document.getElementById("6a68cb85-52ea-4a3d-95ba-e9250aeef4a9");
      if (element == null) {
        console.log("Bokeh: ERROR: autoload.js configured with elementid '6a68cb85-52ea-4a3d-95ba-e9250aeef4a9' but no matching script tag was found. ")
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
                    
                  var docs_json = '{"8cb7bd6e-db99-460f-bf94-47455eddf996":{"roots":{"references":[{"attributes":{"bottom_units":"screen","fill_alpha":{"value":0.5},"fill_color":{"value":"lightgrey"},"left_units":"screen","level":"overlay","line_alpha":{"value":1.0},"line_color":{"value":"black"},"line_dash":[4,4],"line_width":{"value":2},"plot":null,"render_mode":"css","right_units":"screen","top_units":"screen"},"id":"57442ef5-e322-4995-83b1-677fcda6daae","type":"BoxAnnotation"},{"attributes":{},"id":"647b2fc0-9872-48c6-b3cf-f61ac418601e","type":"BasicTickFormatter"},{"attributes":{"source":{"id":"1d3882c1-f62f-4a31-bf12-4712f1ac08ee","type":"ColumnDataSource"}},"id":"e23bc23f-bfdf-40db-9af0-c3c97c1c999f","type":"CDSView"},{"attributes":{},"id":"ad2b5fb5-5291-423d-92d2-357e49676a99","type":"BasicTickFormatter"},{"attributes":{"fill_color":{"value":"white"},"line_color":{"value":"#1f77b4"},"size":{"units":"screen","value":10},"x":{"field":"x"},"y":{"field":"y"}},"id":"02bd1a2a-b0d4-454f-953c-e1ab4ecc927a","type":"Circle"},{"attributes":{},"id":"71a1ac5a-b5ad-42a6-a600-cefbd20b1ded","type":"PanTool"},{"attributes":{"line_alpha":0.1,"line_color":"#1f77b4","line_width":2,"x":{"field":"x"},"y":{"field":"y"}},"id":"9c32fbac-98a5-48e1-a72f-d63acf79bf91","type":"Line"},{"attributes":{"below":[{"id":"3eb01e87-8b69-4e3b-8f02-cd6756395a5e","type":"LinearAxis"}],"left":[{"id":"206986f6-7b59-459b-9ff7-a89d8dade062","type":"LinearAxis"}],"plot_height":300,"plot_width":300,"renderers":[{"id":"3eb01e87-8b69-4e3b-8f02-cd6756395a5e","type":"LinearAxis"},{"id":"24862ee5-3593-462b-a643-19684ca58e23","type":"Grid"},{"id":"206986f6-7b59-459b-9ff7-a89d8dade062","type":"LinearAxis"},{"id":"f411d1d8-c345-487f-9f18-a624d8442d1e","type":"Grid"},{"id":"57442ef5-e322-4995-83b1-677fcda6daae","type":"BoxAnnotation"},{"id":"0e8677ce-1d47-4b7b-9437-f0fb81da2c1c","type":"GlyphRenderer"},{"id":"8a206dba-249c-4bb3-8bfc-2c56a981f139","type":"GlyphRenderer"}],"title":{"id":"ce33d20a-4735-4778-9d5f-29208e4097e4","type":"Title"},"toolbar":{"id":"66b42085-bb89-4465-a0ff-a36aaae5532a","type":"Toolbar"},"x_range":{"id":"ec84a3fd-8924-4e5f-a5b4-28e566bb6d5b","type":"DataRange1d"},"x_scale":{"id":"80f3b793-685c-415f-8c9f-567968de0417","type":"LinearScale"},"y_range":{"id":"efe9718f-da71-4174-8ae9-1d86f8bd8bc0","type":"DataRange1d"},"y_scale":{"id":"ab3a28d9-9506-4658-8dd9-8541a22c95e6","type":"LinearScale"}},"id":"fdcfe9c1-36d5-485c-95ac-636374598bd4","subtype":"Figure","type":"Plot"},{"attributes":{"callback":null,"column_names":["x","y"],"data":{"x":[1,2,3,4,5],"y":[6,7,6,4,5]},"selected":null,"selection_policy":null},"id":"1d3882c1-f62f-4a31-bf12-4712f1ac08ee","type":"ColumnDataSource"},{"attributes":{},"id":"7802b0d3-135b-44e5-ace0-689cf1a5faa5","type":"WheelZoomTool"},{"attributes":{"callback":null},"id":"ec84a3fd-8924-4e5f-a5b4-28e566bb6d5b","type":"DataRange1d"},{"attributes":{"overlay":{"id":"57442ef5-e322-4995-83b1-677fcda6daae","type":"BoxAnnotation"}},"id":"7d091ac0-87b7-4162-bc50-9da335839167","type":"BoxZoomTool"},{"attributes":{"plot":null,"text":"example_bokeh"},"id":"ce33d20a-4735-4778-9d5f-29208e4097e4","type":"Title"},{"attributes":{},"id":"d56b5751-f789-4168-bfac-11d57d94f599","type":"SaveTool"},{"attributes":{},"id":"53b86a1a-5882-4f02-a623-3f540847afa9","type":"ResetTool"},{"attributes":{},"id":"b000c81a-8875-4546-9748-f836099fab73","type":"HelpTool"},{"attributes":{"fill_alpha":{"value":0.1},"fill_color":{"value":"#1f77b4"},"line_alpha":{"value":0.1},"line_color":{"value":"#1f77b4"},"size":{"units":"screen","value":10},"x":{"field":"x"},"y":{"field":"y"}},"id":"0f58b4dd-e063-4abd-8dd1-5fd38d9eda8e","type":"Circle"},{"attributes":{"source":{"id":"e9d7d019-c299-45d7-a9b6-8c91c9fec05e","type":"ColumnDataSource"}},"id":"668b09eb-2cc1-4d0a-99ad-9aa10fb7cb67","type":"CDSView"},{"attributes":{"data_source":{"id":"1d3882c1-f62f-4a31-bf12-4712f1ac08ee","type":"ColumnDataSource"},"glyph":{"id":"fa8441ee-a4ba-440a-b4f6-e5a8e06fae19","type":"Line"},"hover_glyph":null,"muted_glyph":null,"nonselection_glyph":{"id":"9c32fbac-98a5-48e1-a72f-d63acf79bf91","type":"Line"},"selection_glyph":null,"view":{"id":"e23bc23f-bfdf-40db-9af0-c3c97c1c999f","type":"CDSView"}},"id":"0e8677ce-1d47-4b7b-9437-f0fb81da2c1c","type":"GlyphRenderer"},{"attributes":{"callback":null,"column_names":["x","y"],"data":{"x":[1,2,3,4,5],"y":[6,7,6,4,5]},"selected":null,"selection_policy":null},"id":"e9d7d019-c299-45d7-a9b6-8c91c9fec05e","type":"ColumnDataSource"},{"attributes":{"data_source":{"id":"e9d7d019-c299-45d7-a9b6-8c91c9fec05e","type":"ColumnDataSource"},"glyph":{"id":"02bd1a2a-b0d4-454f-953c-e1ab4ecc927a","type":"Circle"},"hover_glyph":null,"muted_glyph":null,"nonselection_glyph":{"id":"0f58b4dd-e063-4abd-8dd1-5fd38d9eda8e","type":"Circle"},"selection_glyph":null,"view":{"id":"668b09eb-2cc1-4d0a-99ad-9aa10fb7cb67","type":"CDSView"}},"id":"8a206dba-249c-4bb3-8bfc-2c56a981f139","type":"GlyphRenderer"},{"attributes":{"active_drag":"auto","active_inspect":"auto","active_scroll":"auto","active_tap":"auto","tools":[{"id":"71a1ac5a-b5ad-42a6-a600-cefbd20b1ded","type":"PanTool"},{"id":"7802b0d3-135b-44e5-ace0-689cf1a5faa5","type":"WheelZoomTool"},{"id":"7d091ac0-87b7-4162-bc50-9da335839167","type":"BoxZoomTool"},{"id":"d56b5751-f789-4168-bfac-11d57d94f599","type":"SaveTool"},{"id":"53b86a1a-5882-4f02-a623-3f540847afa9","type":"ResetTool"},{"id":"b000c81a-8875-4546-9748-f836099fab73","type":"HelpTool"}]},"id":"66b42085-bb89-4465-a0ff-a36aaae5532a","type":"Toolbar"},{"attributes":{},"id":"80f3b793-685c-415f-8c9f-567968de0417","type":"LinearScale"},{"attributes":{"line_color":"#1f77b4","line_width":2,"x":{"field":"x"},"y":{"field":"y"}},"id":"fa8441ee-a4ba-440a-b4f6-e5a8e06fae19","type":"Line"},{"attributes":{},"id":"ab3a28d9-9506-4658-8dd9-8541a22c95e6","type":"LinearScale"},{"attributes":{"formatter":{"id":"647b2fc0-9872-48c6-b3cf-f61ac418601e","type":"BasicTickFormatter"},"plot":{"id":"fdcfe9c1-36d5-485c-95ac-636374598bd4","subtype":"Figure","type":"Plot"},"ticker":{"id":"78cf3e0b-deb5-4d6d-a804-aad8a0f32c78","type":"BasicTicker"}},"id":"206986f6-7b59-459b-9ff7-a89d8dade062","type":"LinearAxis"},{"attributes":{"dimension":1,"plot":{"id":"fdcfe9c1-36d5-485c-95ac-636374598bd4","subtype":"Figure","type":"Plot"},"ticker":{"id":"78cf3e0b-deb5-4d6d-a804-aad8a0f32c78","type":"BasicTicker"}},"id":"f411d1d8-c345-487f-9f18-a624d8442d1e","type":"Grid"},{"attributes":{"formatter":{"id":"ad2b5fb5-5291-423d-92d2-357e49676a99","type":"BasicTickFormatter"},"plot":{"id":"fdcfe9c1-36d5-485c-95ac-636374598bd4","subtype":"Figure","type":"Plot"},"ticker":{"id":"bbc5a545-b0a1-434a-88ca-b06bc0e00023","type":"BasicTicker"}},"id":"3eb01e87-8b69-4e3b-8f02-cd6756395a5e","type":"LinearAxis"},{"attributes":{"callback":null},"id":"efe9718f-da71-4174-8ae9-1d86f8bd8bc0","type":"DataRange1d"},{"attributes":{},"id":"bbc5a545-b0a1-434a-88ca-b06bc0e00023","type":"BasicTicker"},{"attributes":{"plot":{"id":"fdcfe9c1-36d5-485c-95ac-636374598bd4","subtype":"Figure","type":"Plot"},"ticker":{"id":"bbc5a545-b0a1-434a-88ca-b06bc0e00023","type":"BasicTicker"}},"id":"24862ee5-3593-462b-a643-19684ca58e23","type":"Grid"},{"attributes":{},"id":"78cf3e0b-deb5-4d6d-a804-aad8a0f32c78","type":"BasicTicker"}],"root_ids":["fdcfe9c1-36d5-485c-95ac-636374598bd4"]},"title":"Bokeh Application","version":"0.12.15"}}';
                  var render_items = [{"docid":"8cb7bd6e-db99-460f-bf94-47455eddf996","elementid":"6a68cb85-52ea-4a3d-95ba-e9250aeef4a9","modelid":"fdcfe9c1-36d5-485c-95ac-636374598bd4"}];
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