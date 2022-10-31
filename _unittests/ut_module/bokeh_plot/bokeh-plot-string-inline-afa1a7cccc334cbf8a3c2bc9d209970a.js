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
      };var element = document.getElementById("e4a80db4-9103-4ef3-acc0-7a1efbfdc752");
      if (element == null) {
        console.log("Bokeh: ERROR: autoload.js configured with elementid 'e4a80db4-9103-4ef3-acc0-7a1efbfdc752' but no matching script tag was found. ")
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
                    
                  var docs_json = '{"80fd947c-db01-4681-918e-936b985f55a0":{"roots":{"references":[{"attributes":{},"id":"82e1141f-c953-4cf4-939e-62839494fe86","type":"LinearScale"},{"attributes":{"data_source":{"id":"b18cd90f-32fd-4174-804e-ef8e3037d1cd","type":"ColumnDataSource"},"glyph":{"id":"b539db2d-555b-4345-a59a-b6dd4615793c","type":"Line"},"hover_glyph":null,"muted_glyph":null,"nonselection_glyph":{"id":"3c7eb9fe-cc6d-425c-80e2-39a64e587cef","type":"Line"},"selection_glyph":null,"view":{"id":"59dccb28-4e9c-40c7-8e5b-357ce38670f1","type":"CDSView"}},"id":"c6ea817c-a583-4e3e-9424-195166ad047e","type":"GlyphRenderer"},{"attributes":{},"id":"80efd4c2-f989-4069-bd68-1710bb99fba5","type":"PanTool"},{"attributes":{"line_color":"#1f77b4","line_width":2,"x":{"field":"x"},"y":{"field":"y"}},"id":"b539db2d-555b-4345-a59a-b6dd4615793c","type":"Line"},{"attributes":{},"id":"4287245f-00f7-4654-b4be-8dbe1ce296f0","type":"WheelZoomTool"},{"attributes":{"line_alpha":0.1,"line_color":"#1f77b4","line_width":2,"x":{"field":"x"},"y":{"field":"y"}},"id":"3c7eb9fe-cc6d-425c-80e2-39a64e587cef","type":"Line"},{"attributes":{"overlay":{"id":"c7c30b38-4a35-4507-872c-adaef7bc4b1d","type":"BoxAnnotation"}},"id":"cbd9e671-1554-48d5-99a8-023390abe9d7","type":"BoxZoomTool"},{"attributes":{},"id":"ffc72cfc-58cc-4f7c-8659-b47e344a780f","type":"SaveTool"},{"attributes":{},"id":"4510c86d-2899-4e60-b540-4139c90beb82","type":"LinearScale"},{"attributes":{},"id":"8462d4d2-ebd5-4b65-ac1b-d04d9184b2d2","type":"ResetTool"},{"attributes":{},"id":"e082a759-fcb9-4a34-82c2-3fa39d1639f7","type":"HelpTool"},{"attributes":{"callback":null},"id":"6a8f4233-a3ac-4ceb-b2c1-fc3cd4273c4f","type":"DataRange1d"},{"attributes":{"data_source":{"id":"d4db0497-f028-4520-9e74-149c45887f68","type":"ColumnDataSource"},"glyph":{"id":"16346b39-7c8a-4e70-8b56-9d0100984f7f","type":"Circle"},"hover_glyph":null,"muted_glyph":null,"nonselection_glyph":{"id":"3a8692b2-39e4-4c11-bc29-eee5ad727c9f","type":"Circle"},"selection_glyph":null,"view":{"id":"13159bb4-283c-4aab-8397-e4eed26597b1","type":"CDSView"}},"id":"0f865ded-ec1b-4df2-81b5-e4e4404311ca","type":"GlyphRenderer"},{"attributes":{"source":{"id":"d4db0497-f028-4520-9e74-149c45887f68","type":"ColumnDataSource"}},"id":"13159bb4-283c-4aab-8397-e4eed26597b1","type":"CDSView"},{"attributes":{"fill_color":{"value":"white"},"line_color":{"value":"#1f77b4"},"size":{"units":"screen","value":10},"x":{"field":"x"},"y":{"field":"y"}},"id":"16346b39-7c8a-4e70-8b56-9d0100984f7f","type":"Circle"},{"attributes":{"callback":null,"column_names":["x","y"],"data":{"x":[1,2,3,4,5],"y":[6,7,6,4,5]},"selected":null,"selection_policy":null},"id":"d4db0497-f028-4520-9e74-149c45887f68","type":"ColumnDataSource"},{"attributes":{"active_drag":"auto","active_inspect":"auto","active_scroll":"auto","active_tap":"auto","tools":[{"id":"80efd4c2-f989-4069-bd68-1710bb99fba5","type":"PanTool"},{"id":"4287245f-00f7-4654-b4be-8dbe1ce296f0","type":"WheelZoomTool"},{"id":"cbd9e671-1554-48d5-99a8-023390abe9d7","type":"BoxZoomTool"},{"id":"ffc72cfc-58cc-4f7c-8659-b47e344a780f","type":"SaveTool"},{"id":"8462d4d2-ebd5-4b65-ac1b-d04d9184b2d2","type":"ResetTool"},{"id":"e082a759-fcb9-4a34-82c2-3fa39d1639f7","type":"HelpTool"}]},"id":"21f08016-7ebb-4660-aa68-27ce08522aae","type":"Toolbar"},{"attributes":{"fill_alpha":{"value":0.1},"fill_color":{"value":"#1f77b4"},"line_alpha":{"value":0.1},"line_color":{"value":"#1f77b4"},"size":{"units":"screen","value":10},"x":{"field":"x"},"y":{"field":"y"}},"id":"3a8692b2-39e4-4c11-bc29-eee5ad727c9f","type":"Circle"},{"attributes":{"source":{"id":"b18cd90f-32fd-4174-804e-ef8e3037d1cd","type":"ColumnDataSource"}},"id":"59dccb28-4e9c-40c7-8e5b-357ce38670f1","type":"CDSView"},{"attributes":{"plot":null,"text":"example_bokeh"},"id":"f11a2e2d-1061-42fb-a2ef-dfc91c32de40","type":"Title"},{"attributes":{"plot":{"id":"fca6b596-7007-423e-ba16-c728574c6fff","subtype":"Figure","type":"Plot"},"ticker":{"id":"249767f8-8611-4f3a-a632-87a44786a1c0","type":"BasicTicker"}},"id":"1e308f1c-e353-42b9-990f-c310ce74a161","type":"Grid"},{"attributes":{"formatter":{"id":"2ae1521c-c6a7-4bab-b891-9fa29d999135","type":"BasicTickFormatter"},"plot":{"id":"fca6b596-7007-423e-ba16-c728574c6fff","subtype":"Figure","type":"Plot"},"ticker":{"id":"ff843260-655e-437d-89b4-0b0897492588","type":"BasicTicker"}},"id":"47a70b40-ac42-4d53-80fe-14846ed268e0","type":"LinearAxis"},{"attributes":{"callback":null,"column_names":["x","y"],"data":{"x":[1,2,3,4,5],"y":[6,7,6,4,5]},"selected":null,"selection_policy":null},"id":"b18cd90f-32fd-4174-804e-ef8e3037d1cd","type":"ColumnDataSource"},{"attributes":{"below":[{"id":"3428f767-bbcf-42df-9809-c2664ffe547e","type":"LinearAxis"}],"left":[{"id":"47a70b40-ac42-4d53-80fe-14846ed268e0","type":"LinearAxis"}],"plot_height":300,"plot_width":300,"renderers":[{"id":"3428f767-bbcf-42df-9809-c2664ffe547e","type":"LinearAxis"},{"id":"1e308f1c-e353-42b9-990f-c310ce74a161","type":"Grid"},{"id":"47a70b40-ac42-4d53-80fe-14846ed268e0","type":"LinearAxis"},{"id":"a43f0012-6767-439f-84b4-c700a4c24040","type":"Grid"},{"id":"c7c30b38-4a35-4507-872c-adaef7bc4b1d","type":"BoxAnnotation"},{"id":"c6ea817c-a583-4e3e-9424-195166ad047e","type":"GlyphRenderer"},{"id":"0f865ded-ec1b-4df2-81b5-e4e4404311ca","type":"GlyphRenderer"}],"title":{"id":"f11a2e2d-1061-42fb-a2ef-dfc91c32de40","type":"Title"},"toolbar":{"id":"21f08016-7ebb-4660-aa68-27ce08522aae","type":"Toolbar"},"x_range":{"id":"1e265107-8082-4098-92c9-dba38cbdd4ed","type":"DataRange1d"},"x_scale":{"id":"4510c86d-2899-4e60-b540-4139c90beb82","type":"LinearScale"},"y_range":{"id":"6a8f4233-a3ac-4ceb-b2c1-fc3cd4273c4f","type":"DataRange1d"},"y_scale":{"id":"82e1141f-c953-4cf4-939e-62839494fe86","type":"LinearScale"}},"id":"fca6b596-7007-423e-ba16-c728574c6fff","subtype":"Figure","type":"Plot"},{"attributes":{"callback":null},"id":"1e265107-8082-4098-92c9-dba38cbdd4ed","type":"DataRange1d"},{"attributes":{"formatter":{"id":"12840eaf-b417-4f0d-947f-34aefdbfe9e4","type":"BasicTickFormatter"},"plot":{"id":"fca6b596-7007-423e-ba16-c728574c6fff","subtype":"Figure","type":"Plot"},"ticker":{"id":"249767f8-8611-4f3a-a632-87a44786a1c0","type":"BasicTicker"}},"id":"3428f767-bbcf-42df-9809-c2664ffe547e","type":"LinearAxis"},{"attributes":{},"id":"12840eaf-b417-4f0d-947f-34aefdbfe9e4","type":"BasicTickFormatter"},{"attributes":{},"id":"249767f8-8611-4f3a-a632-87a44786a1c0","type":"BasicTicker"},{"attributes":{},"id":"ff843260-655e-437d-89b4-0b0897492588","type":"BasicTicker"},{"attributes":{"dimension":1,"plot":{"id":"fca6b596-7007-423e-ba16-c728574c6fff","subtype":"Figure","type":"Plot"},"ticker":{"id":"ff843260-655e-437d-89b4-0b0897492588","type":"BasicTicker"}},"id":"a43f0012-6767-439f-84b4-c700a4c24040","type":"Grid"},{"attributes":{"bottom_units":"screen","fill_alpha":{"value":0.5},"fill_color":{"value":"lightgrey"},"left_units":"screen","level":"overlay","line_alpha":{"value":1.0},"line_color":{"value":"black"},"line_dash":[4,4],"line_width":{"value":2},"plot":null,"render_mode":"css","right_units":"screen","top_units":"screen"},"id":"c7c30b38-4a35-4507-872c-adaef7bc4b1d","type":"BoxAnnotation"},{"attributes":{},"id":"2ae1521c-c6a7-4bab-b891-9fa29d999135","type":"BasicTickFormatter"}],"root_ids":["fca6b596-7007-423e-ba16-c728574c6fff"]},"title":"Bokeh Application","version":"0.12.15"}}';
                  var render_items = [{"docid":"80fd947c-db01-4681-918e-936b985f55a0","elementid":"e4a80db4-9103-4ef3-acc0-7a1efbfdc752","modelid":"fca6b596-7007-423e-ba16-c728574c6fff"}];
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