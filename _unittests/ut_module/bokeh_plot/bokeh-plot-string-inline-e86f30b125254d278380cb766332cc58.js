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
      };var element = document.getElementById("fcf13404-3680-4b6c-a3c3-c3be6ac065d6");
      if (element == null) {
        console.log("Bokeh: ERROR: autoload.js configured with elementid 'fcf13404-3680-4b6c-a3c3-c3be6ac065d6' but no matching script tag was found. ")
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
                    
                  var docs_json = '{"2d66fb97-5224-4175-8972-a3a9af860ae3":{"roots":{"references":[{"attributes":{"plot":{"id":"1199640f-7f63-463e-952a-5f1fd2720668","subtype":"Figure","type":"Plot"},"ticker":{"id":"7a275098-91ff-412b-a740-1ce45f72cd35","type":"BasicTicker"}},"id":"250e7591-10db-4a47-9eaa-2cad3879e2bb","type":"Grid"},{"attributes":{"data_source":{"id":"799a5cd4-74a5-448d-b638-6c50f9595505","type":"ColumnDataSource"},"glyph":{"id":"48ba5fa5-558a-4a4d-a310-a0fe23f05f0f","type":"Line"},"hover_glyph":null,"muted_glyph":null,"nonselection_glyph":{"id":"9441b046-542d-45f3-a719-d4e8c90d0625","type":"Line"},"selection_glyph":null,"view":{"id":"f5023c5f-97e9-4477-8a74-820b5a5e5e0f","type":"CDSView"}},"id":"804c935f-1443-4516-ba98-51171c1043fb","type":"GlyphRenderer"},{"attributes":{"line_color":"#1f77b4","line_width":2,"x":{"field":"x"},"y":{"field":"y"}},"id":"48ba5fa5-558a-4a4d-a310-a0fe23f05f0f","type":"Line"},{"attributes":{"formatter":{"id":"6b1af755-d8c7-4567-9ae9-458b211a9603","type":"BasicTickFormatter"},"plot":{"id":"1199640f-7f63-463e-952a-5f1fd2720668","subtype":"Figure","type":"Plot"},"ticker":{"id":"7a275098-91ff-412b-a740-1ce45f72cd35","type":"BasicTicker"}},"id":"5a9b39d6-5fa2-4f20-bbd1-86bba73dadd7","type":"LinearAxis"},{"attributes":{"plot":null,"text":"example_bokeh"},"id":"d95bcb4a-90c3-45fe-8e3c-7c703e806c3c","type":"Title"},{"attributes":{"callback":null,"column_names":["x","y"],"data":{"x":[1,2,3,4,5],"y":[6,7,6,4,5]},"selected":null,"selection_policy":null},"id":"44211309-db17-410d-a7ba-13e9fa5cc07b","type":"ColumnDataSource"},{"attributes":{},"id":"7a275098-91ff-412b-a740-1ce45f72cd35","type":"BasicTicker"},{"attributes":{"line_alpha":0.1,"line_color":"#1f77b4","line_width":2,"x":{"field":"x"},"y":{"field":"y"}},"id":"9441b046-542d-45f3-a719-d4e8c90d0625","type":"Line"},{"attributes":{},"id":"04e5f1ff-19ad-470b-944e-8a5f75a838a8","type":"BasicTicker"},{"attributes":{"active_drag":"auto","active_inspect":"auto","active_scroll":"auto","active_tap":"auto","tools":[{"id":"a9c7fa6e-7354-44ad-b953-1fc297e313fc","type":"PanTool"},{"id":"21df4bf3-a775-4e13-aaef-89035390b6c4","type":"WheelZoomTool"},{"id":"dbdb5558-8c75-4f9f-8528-92b75e6764b9","type":"BoxZoomTool"},{"id":"a906b624-6583-4aa9-98d4-bf89f1cc2490","type":"SaveTool"},{"id":"5870326e-90f1-44b8-8b0d-533ad8eb45c9","type":"ResetTool"},{"id":"6d65ea74-88f4-48f6-8624-580e2344428c","type":"HelpTool"}]},"id":"37a89367-ad6c-41a0-9556-d61ce230de48","type":"Toolbar"},{"attributes":{"dimension":1,"plot":{"id":"1199640f-7f63-463e-952a-5f1fd2720668","subtype":"Figure","type":"Plot"},"ticker":{"id":"04e5f1ff-19ad-470b-944e-8a5f75a838a8","type":"BasicTicker"}},"id":"058efb1e-0d4a-4776-880e-689f743b1ed0","type":"Grid"},{"attributes":{"bottom_units":"screen","fill_alpha":{"value":0.5},"fill_color":{"value":"lightgrey"},"left_units":"screen","level":"overlay","line_alpha":{"value":1.0},"line_color":{"value":"black"},"line_dash":[4,4],"line_width":{"value":2},"plot":null,"render_mode":"css","right_units":"screen","top_units":"screen"},"id":"7391d612-b7c5-4cc2-87d8-118c612535d8","type":"BoxAnnotation"},{"attributes":{},"id":"6b1af755-d8c7-4567-9ae9-458b211a9603","type":"BasicTickFormatter"},{"attributes":{"callback":null},"id":"a5b4bf5a-3cce-43e6-958a-40dbf82ec2cd","type":"DataRange1d"},{"attributes":{},"id":"a9c7fa6e-7354-44ad-b953-1fc297e313fc","type":"PanTool"},{"attributes":{},"id":"21df4bf3-a775-4e13-aaef-89035390b6c4","type":"WheelZoomTool"},{"attributes":{"overlay":{"id":"7391d612-b7c5-4cc2-87d8-118c612535d8","type":"BoxAnnotation"}},"id":"dbdb5558-8c75-4f9f-8528-92b75e6764b9","type":"BoxZoomTool"},{"attributes":{},"id":"a556b679-3ad6-448e-a321-8a89e4fa8931","type":"LinearScale"},{"attributes":{},"id":"a906b624-6583-4aa9-98d4-bf89f1cc2490","type":"SaveTool"},{"attributes":{},"id":"5870326e-90f1-44b8-8b0d-533ad8eb45c9","type":"ResetTool"},{"attributes":{"below":[{"id":"5a9b39d6-5fa2-4f20-bbd1-86bba73dadd7","type":"LinearAxis"}],"left":[{"id":"0df5a283-65e0-4d31-8594-cb6329b31a95","type":"LinearAxis"}],"plot_height":300,"plot_width":300,"renderers":[{"id":"5a9b39d6-5fa2-4f20-bbd1-86bba73dadd7","type":"LinearAxis"},{"id":"250e7591-10db-4a47-9eaa-2cad3879e2bb","type":"Grid"},{"id":"0df5a283-65e0-4d31-8594-cb6329b31a95","type":"LinearAxis"},{"id":"058efb1e-0d4a-4776-880e-689f743b1ed0","type":"Grid"},{"id":"7391d612-b7c5-4cc2-87d8-118c612535d8","type":"BoxAnnotation"},{"id":"804c935f-1443-4516-ba98-51171c1043fb","type":"GlyphRenderer"},{"id":"ac78d733-3e42-44de-872e-49e7d6cb857e","type":"GlyphRenderer"}],"title":{"id":"d95bcb4a-90c3-45fe-8e3c-7c703e806c3c","type":"Title"},"toolbar":{"id":"37a89367-ad6c-41a0-9556-d61ce230de48","type":"Toolbar"},"x_range":{"id":"2dda12fb-3336-49de-a88d-82fcd8405424","type":"DataRange1d"},"x_scale":{"id":"a556b679-3ad6-448e-a321-8a89e4fa8931","type":"LinearScale"},"y_range":{"id":"a5b4bf5a-3cce-43e6-958a-40dbf82ec2cd","type":"DataRange1d"},"y_scale":{"id":"d0fd03fc-c0ab-4b6d-ae7b-c84b28758283","type":"LinearScale"}},"id":"1199640f-7f63-463e-952a-5f1fd2720668","subtype":"Figure","type":"Plot"},{"attributes":{},"id":"6d65ea74-88f4-48f6-8624-580e2344428c","type":"HelpTool"},{"attributes":{"callback":null,"column_names":["x","y"],"data":{"x":[1,2,3,4,5],"y":[6,7,6,4,5]},"selected":null,"selection_policy":null},"id":"799a5cd4-74a5-448d-b638-6c50f9595505","type":"ColumnDataSource"},{"attributes":{},"id":"5a9e46c6-3eff-4115-a20c-6a50f36c25e2","type":"BasicTickFormatter"},{"attributes":{"source":{"id":"799a5cd4-74a5-448d-b638-6c50f9595505","type":"ColumnDataSource"}},"id":"f5023c5f-97e9-4477-8a74-820b5a5e5e0f","type":"CDSView"},{"attributes":{"callback":null},"id":"2dda12fb-3336-49de-a88d-82fcd8405424","type":"DataRange1d"},{"attributes":{"source":{"id":"44211309-db17-410d-a7ba-13e9fa5cc07b","type":"ColumnDataSource"}},"id":"49e8e24c-1c10-4ed4-a863-8440b6c8215e","type":"CDSView"},{"attributes":{"fill_color":{"value":"white"},"line_color":{"value":"#1f77b4"},"size":{"units":"screen","value":10},"x":{"field":"x"},"y":{"field":"y"}},"id":"f034790b-55e5-419e-a87b-36b70e25e96c","type":"Circle"},{"attributes":{"fill_alpha":{"value":0.1},"fill_color":{"value":"#1f77b4"},"line_alpha":{"value":0.1},"line_color":{"value":"#1f77b4"},"size":{"units":"screen","value":10},"x":{"field":"x"},"y":{"field":"y"}},"id":"8f10e3b6-63de-46bb-b6ac-4a88169bc5f3","type":"Circle"},{"attributes":{"data_source":{"id":"44211309-db17-410d-a7ba-13e9fa5cc07b","type":"ColumnDataSource"},"glyph":{"id":"f034790b-55e5-419e-a87b-36b70e25e96c","type":"Circle"},"hover_glyph":null,"muted_glyph":null,"nonselection_glyph":{"id":"8f10e3b6-63de-46bb-b6ac-4a88169bc5f3","type":"Circle"},"selection_glyph":null,"view":{"id":"49e8e24c-1c10-4ed4-a863-8440b6c8215e","type":"CDSView"}},"id":"ac78d733-3e42-44de-872e-49e7d6cb857e","type":"GlyphRenderer"},{"attributes":{},"id":"d0fd03fc-c0ab-4b6d-ae7b-c84b28758283","type":"LinearScale"},{"attributes":{"formatter":{"id":"5a9e46c6-3eff-4115-a20c-6a50f36c25e2","type":"BasicTickFormatter"},"plot":{"id":"1199640f-7f63-463e-952a-5f1fd2720668","subtype":"Figure","type":"Plot"},"ticker":{"id":"04e5f1ff-19ad-470b-944e-8a5f75a838a8","type":"BasicTicker"}},"id":"0df5a283-65e0-4d31-8594-cb6329b31a95","type":"LinearAxis"}],"root_ids":["1199640f-7f63-463e-952a-5f1fd2720668"]},"title":"Bokeh Application","version":"0.12.15"}}';
                  var render_items = [{"docid":"2d66fb97-5224-4175-8972-a3a9af860ae3","elementid":"fcf13404-3680-4b6c-a3c3-c3be6ac065d6","modelid":"1199640f-7f63-463e-952a-5f1fd2720668"}];
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