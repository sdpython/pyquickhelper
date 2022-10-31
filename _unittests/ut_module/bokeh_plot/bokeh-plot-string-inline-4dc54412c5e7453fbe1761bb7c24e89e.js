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
      };var element = document.getElementById("7e6a3828-cc6c-4b3d-861e-9053e46fad03");
      if (element == null) {
        console.log("Bokeh: ERROR: autoload.js configured with elementid '7e6a3828-cc6c-4b3d-861e-9053e46fad03' but no matching script tag was found. ")
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
                    
                  var docs_json = '{"bc89122b-7902-48a8-ab72-bbd6a386ef79":{"roots":{"references":[{"attributes":{"data_source":{"id":"d20de3f7-682f-4ed9-9f79-0e4fb44d28a3","type":"ColumnDataSource"},"glyph":{"id":"37d858cb-b846-4a74-a9a4-742d612cd580","type":"Line"},"hover_glyph":null,"muted_glyph":null,"nonselection_glyph":{"id":"34b08d4c-6f63-4f1d-96f0-aad3466b0f0c","type":"Line"},"selection_glyph":null,"view":{"id":"2a7cb0b0-7eff-41dc-b65f-2f574aa63922","type":"CDSView"}},"id":"34d43df3-16a6-4e96-a233-d7dc99f68d80","type":"GlyphRenderer"},{"attributes":{},"id":"020cf6e6-7f5d-4844-87ac-a8c6b0ab98eb","type":"PanTool"},{"attributes":{"line_color":"#1f77b4","line_width":2,"x":{"field":"x"},"y":{"field":"y"}},"id":"37d858cb-b846-4a74-a9a4-742d612cd580","type":"Line"},{"attributes":{},"id":"5d4e1ae1-61a6-4c66-a2b0-b180d9264d5d","type":"WheelZoomTool"},{"attributes":{"line_alpha":0.1,"line_color":"#1f77b4","line_width":2,"x":{"field":"x"},"y":{"field":"y"}},"id":"34b08d4c-6f63-4f1d-96f0-aad3466b0f0c","type":"Line"},{"attributes":{"overlay":{"id":"a27dc69f-0ccc-4720-b66d-46e61d7c543c","type":"BoxAnnotation"}},"id":"55df92fa-1608-4bd4-a4d0-e30d54b0cb46","type":"BoxZoomTool"},{"attributes":{},"id":"268e8a2c-9096-48a9-bf32-4ec596f75bd9","type":"SaveTool"},{"attributes":{},"id":"64b503f3-1063-40af-ac65-cb59ac715182","type":"LinearScale"},{"attributes":{},"id":"2bf8ed56-f15b-4d1e-a308-7e9a9ce2f3b2","type":"ResetTool"},{"attributes":{},"id":"f0450fb0-cfd4-4034-b4f4-81d2f52e6afa","type":"HelpTool"},{"attributes":{},"id":"61e1c549-36bb-424e-ad47-ec49da82c3cb","type":"LinearScale"},{"attributes":{"callback":null},"id":"62ef9579-afba-4c33-8908-cb7430b1779c","type":"DataRange1d"},{"attributes":{"data_source":{"id":"30e88fb1-c33b-495a-b28d-899b75813882","type":"ColumnDataSource"},"glyph":{"id":"10a70b48-8113-4f9d-a968-19b5e3230155","type":"Circle"},"hover_glyph":null,"muted_glyph":null,"nonselection_glyph":{"id":"78b75187-4da4-46e2-9614-bb3c38a89e3f","type":"Circle"},"selection_glyph":null,"view":{"id":"dd4131f2-32bd-4e0a-8cfe-97ca878b087f","type":"CDSView"}},"id":"07af8212-cd5c-4cfb-ba97-c6abae54dfcd","type":"GlyphRenderer"},{"attributes":{"source":{"id":"30e88fb1-c33b-495a-b28d-899b75813882","type":"ColumnDataSource"}},"id":"dd4131f2-32bd-4e0a-8cfe-97ca878b087f","type":"CDSView"},{"attributes":{},"id":"a2452540-54ab-4d78-83fe-4d1f29a2bad6","type":"BasicTickFormatter"},{"attributes":{"fill_color":{"value":"white"},"line_color":{"value":"#1f77b4"},"size":{"units":"screen","value":10},"x":{"field":"x"},"y":{"field":"y"}},"id":"10a70b48-8113-4f9d-a968-19b5e3230155","type":"Circle"},{"attributes":{"callback":null,"column_names":["x","y"],"data":{"x":[1,2,3,4,5],"y":[6,7,6,4,5]},"selected":null,"selection_policy":null},"id":"30e88fb1-c33b-495a-b28d-899b75813882","type":"ColumnDataSource"},{"attributes":{"active_drag":"auto","active_inspect":"auto","active_scroll":"auto","active_tap":"auto","tools":[{"id":"020cf6e6-7f5d-4844-87ac-a8c6b0ab98eb","type":"PanTool"},{"id":"5d4e1ae1-61a6-4c66-a2b0-b180d9264d5d","type":"WheelZoomTool"},{"id":"55df92fa-1608-4bd4-a4d0-e30d54b0cb46","type":"BoxZoomTool"},{"id":"268e8a2c-9096-48a9-bf32-4ec596f75bd9","type":"SaveTool"},{"id":"2bf8ed56-f15b-4d1e-a308-7e9a9ce2f3b2","type":"ResetTool"},{"id":"f0450fb0-cfd4-4034-b4f4-81d2f52e6afa","type":"HelpTool"}]},"id":"90b615e6-7d12-4976-b45b-52319ebba94f","type":"Toolbar"},{"attributes":{"fill_alpha":{"value":0.1},"fill_color":{"value":"#1f77b4"},"line_alpha":{"value":0.1},"line_color":{"value":"#1f77b4"},"size":{"units":"screen","value":10},"x":{"field":"x"},"y":{"field":"y"}},"id":"78b75187-4da4-46e2-9614-bb3c38a89e3f","type":"Circle"},{"attributes":{"source":{"id":"d20de3f7-682f-4ed9-9f79-0e4fb44d28a3","type":"ColumnDataSource"}},"id":"2a7cb0b0-7eff-41dc-b65f-2f574aa63922","type":"CDSView"},{"attributes":{"plot":null,"text":"example_bokeh"},"id":"65160898-a3d2-4259-aafd-f8fa5858fa64","type":"Title"},{"attributes":{"plot":{"id":"c02a372f-e39e-4d23-9553-399f325f4f35","subtype":"Figure","type":"Plot"},"ticker":{"id":"6cc65cbe-4a2d-4092-8f4e-5c6de26217a1","type":"BasicTicker"}},"id":"5c967660-d16e-4844-9318-7d6e734005f9","type":"Grid"},{"attributes":{"formatter":{"id":"a2452540-54ab-4d78-83fe-4d1f29a2bad6","type":"BasicTickFormatter"},"plot":{"id":"c02a372f-e39e-4d23-9553-399f325f4f35","subtype":"Figure","type":"Plot"},"ticker":{"id":"8be24694-f271-4746-a6bd-ed62ea12a760","type":"BasicTicker"}},"id":"9192fc6f-c6a1-4416-b568-40498e9be4c2","type":"LinearAxis"},{"attributes":{"callback":null,"column_names":["x","y"],"data":{"x":[1,2,3,4,5],"y":[6,7,6,4,5]},"selected":null,"selection_policy":null},"id":"d20de3f7-682f-4ed9-9f79-0e4fb44d28a3","type":"ColumnDataSource"},{"attributes":{"below":[{"id":"ff37686a-e392-42e8-9fc9-f63dfa7c8bf4","type":"LinearAxis"}],"left":[{"id":"9192fc6f-c6a1-4416-b568-40498e9be4c2","type":"LinearAxis"}],"plot_height":300,"plot_width":300,"renderers":[{"id":"ff37686a-e392-42e8-9fc9-f63dfa7c8bf4","type":"LinearAxis"},{"id":"5c967660-d16e-4844-9318-7d6e734005f9","type":"Grid"},{"id":"9192fc6f-c6a1-4416-b568-40498e9be4c2","type":"LinearAxis"},{"id":"18bc66cc-76f0-47f4-965d-daf4cefd48e0","type":"Grid"},{"id":"a27dc69f-0ccc-4720-b66d-46e61d7c543c","type":"BoxAnnotation"},{"id":"34d43df3-16a6-4e96-a233-d7dc99f68d80","type":"GlyphRenderer"},{"id":"07af8212-cd5c-4cfb-ba97-c6abae54dfcd","type":"GlyphRenderer"}],"title":{"id":"65160898-a3d2-4259-aafd-f8fa5858fa64","type":"Title"},"toolbar":{"id":"90b615e6-7d12-4976-b45b-52319ebba94f","type":"Toolbar"},"x_range":{"id":"de6062d8-f325-4d9b-9faf-eb9f8d146b00","type":"DataRange1d"},"x_scale":{"id":"61e1c549-36bb-424e-ad47-ec49da82c3cb","type":"LinearScale"},"y_range":{"id":"62ef9579-afba-4c33-8908-cb7430b1779c","type":"DataRange1d"},"y_scale":{"id":"64b503f3-1063-40af-ac65-cb59ac715182","type":"LinearScale"}},"id":"c02a372f-e39e-4d23-9553-399f325f4f35","subtype":"Figure","type":"Plot"},{"attributes":{"callback":null},"id":"de6062d8-f325-4d9b-9faf-eb9f8d146b00","type":"DataRange1d"},{"attributes":{"formatter":{"id":"ee2fc194-ce50-4304-b4eb-14b10fe3beaf","type":"BasicTickFormatter"},"plot":{"id":"c02a372f-e39e-4d23-9553-399f325f4f35","subtype":"Figure","type":"Plot"},"ticker":{"id":"6cc65cbe-4a2d-4092-8f4e-5c6de26217a1","type":"BasicTicker"}},"id":"ff37686a-e392-42e8-9fc9-f63dfa7c8bf4","type":"LinearAxis"},{"attributes":{},"id":"ee2fc194-ce50-4304-b4eb-14b10fe3beaf","type":"BasicTickFormatter"},{"attributes":{},"id":"6cc65cbe-4a2d-4092-8f4e-5c6de26217a1","type":"BasicTicker"},{"attributes":{},"id":"8be24694-f271-4746-a6bd-ed62ea12a760","type":"BasicTicker"},{"attributes":{"dimension":1,"plot":{"id":"c02a372f-e39e-4d23-9553-399f325f4f35","subtype":"Figure","type":"Plot"},"ticker":{"id":"8be24694-f271-4746-a6bd-ed62ea12a760","type":"BasicTicker"}},"id":"18bc66cc-76f0-47f4-965d-daf4cefd48e0","type":"Grid"},{"attributes":{"bottom_units":"screen","fill_alpha":{"value":0.5},"fill_color":{"value":"lightgrey"},"left_units":"screen","level":"overlay","line_alpha":{"value":1.0},"line_color":{"value":"black"},"line_dash":[4,4],"line_width":{"value":2},"plot":null,"render_mode":"css","right_units":"screen","top_units":"screen"},"id":"a27dc69f-0ccc-4720-b66d-46e61d7c543c","type":"BoxAnnotation"}],"root_ids":["c02a372f-e39e-4d23-9553-399f325f4f35"]},"title":"Bokeh Application","version":"0.12.15"}}';
                  var render_items = [{"docid":"bc89122b-7902-48a8-ab72-bbd6a386ef79","elementid":"7e6a3828-cc6c-4b3d-861e-9053e46fad03","modelid":"c02a372f-e39e-4d23-9553-399f325f4f35"}];
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