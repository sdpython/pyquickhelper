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
      };var element = document.getElementById("62c35d67-5a81-482a-8bf7-06c626647e00");
      if (element == null) {
        console.log("Bokeh: ERROR: autoload.js configured with elementid '62c35d67-5a81-482a-8bf7-06c626647e00' but no matching script tag was found. ")
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
                    
                  var docs_json = '{"c875d55d-486c-4026-9692-ae7fe7379059":{"roots":{"references":[{"attributes":{"formatter":{"id":"402a8433-82fa-49d0-a645-19a789197ec2","type":"BasicTickFormatter"},"plot":{"id":"bc9b3dad-277d-4218-aeab-7dbead17f708","subtype":"Figure","type":"Plot"},"ticker":{"id":"2b4f37d1-e015-4255-a440-eb9d21f54b96","type":"BasicTicker"}},"id":"0e9937f6-8312-4b54-ab8e-5f2fb67c8aad","type":"LinearAxis"},{"attributes":{"data_source":{"id":"81260ee0-4f83-4090-80c0-3e4f4e2a6d0d","type":"ColumnDataSource"},"glyph":{"id":"74845e1c-9099-4b86-b697-02f808e53a72","type":"Line"},"hover_glyph":null,"muted_glyph":null,"nonselection_glyph":{"id":"edf280c2-162b-4836-95c6-eef0a168e7b6","type":"Line"},"selection_glyph":null,"view":{"id":"ea452543-68b8-4b0c-bfc9-660abf79facd","type":"CDSView"}},"id":"fa819c9f-3b1f-4ff2-a07a-7767f5e6f5ce","type":"GlyphRenderer"},{"attributes":{},"id":"2dbd085a-470c-4164-b5ad-53937b02569f","type":"BasicTickFormatter"},{"attributes":{"below":[{"id":"71730669-4a36-4de6-911a-f3a33e63cc36","type":"LinearAxis"}],"left":[{"id":"0e9937f6-8312-4b54-ab8e-5f2fb67c8aad","type":"LinearAxis"}],"plot_height":300,"plot_width":300,"renderers":[{"id":"71730669-4a36-4de6-911a-f3a33e63cc36","type":"LinearAxis"},{"id":"0765ee2b-22cf-4808-a2f1-7074b0069f9f","type":"Grid"},{"id":"0e9937f6-8312-4b54-ab8e-5f2fb67c8aad","type":"LinearAxis"},{"id":"5d9be529-ce3e-47be-a922-51cc3bddab20","type":"Grid"},{"id":"6b5388f9-204b-4f91-91cc-3deb63267fbd","type":"BoxAnnotation"},{"id":"fa819c9f-3b1f-4ff2-a07a-7767f5e6f5ce","type":"GlyphRenderer"},{"id":"4b0e4132-a10e-403e-9c09-eee59627a869","type":"GlyphRenderer"}],"title":{"id":"76bdf638-48a1-4c5c-81b1-ce570b82309d","type":"Title"},"toolbar":{"id":"c3fb1b7b-682a-41b6-a89c-250d3c7073c1","type":"Toolbar"},"x_range":{"id":"7a07edc8-cd10-4f86-9fbb-250af003303a","type":"DataRange1d"},"x_scale":{"id":"18afe01f-55f8-4179-8bf3-649becff4c1e","type":"LinearScale"},"y_range":{"id":"b6467629-cc28-49f2-97b4-858ec7701a0e","type":"DataRange1d"},"y_scale":{"id":"a4000736-97ab-4f76-9c55-66ed35581caa","type":"LinearScale"}},"id":"bc9b3dad-277d-4218-aeab-7dbead17f708","subtype":"Figure","type":"Plot"},{"attributes":{},"id":"2b4f37d1-e015-4255-a440-eb9d21f54b96","type":"BasicTicker"},{"attributes":{"line_color":"#1f77b4","line_width":2,"x":{"field":"x"},"y":{"field":"y"}},"id":"74845e1c-9099-4b86-b697-02f808e53a72","type":"Line"},{"attributes":{"dimension":1,"plot":{"id":"bc9b3dad-277d-4218-aeab-7dbead17f708","subtype":"Figure","type":"Plot"},"ticker":{"id":"2b4f37d1-e015-4255-a440-eb9d21f54b96","type":"BasicTicker"}},"id":"5d9be529-ce3e-47be-a922-51cc3bddab20","type":"Grid"},{"attributes":{"active_drag":"auto","active_inspect":"auto","active_scroll":"auto","active_tap":"auto","tools":[{"id":"85b98586-c5f7-4299-9d9c-90227fd7f25f","type":"PanTool"},{"id":"13b54b0d-071b-44db-9ea4-7c1bc6d7aafe","type":"WheelZoomTool"},{"id":"e413d83e-8697-4222-8b44-3f7283a67afc","type":"BoxZoomTool"},{"id":"4fe95fc0-9c0a-4101-9064-d6b423968e17","type":"SaveTool"},{"id":"782a6afa-ee79-4df9-bb6e-aa29e9c5ac28","type":"ResetTool"},{"id":"b00273c8-1859-42f5-9adb-9fe04e912e09","type":"HelpTool"}]},"id":"c3fb1b7b-682a-41b6-a89c-250d3c7073c1","type":"Toolbar"},{"attributes":{"bottom_units":"screen","fill_alpha":{"value":0.5},"fill_color":{"value":"lightgrey"},"left_units":"screen","level":"overlay","line_alpha":{"value":1.0},"line_color":{"value":"black"},"line_dash":[4,4],"line_width":{"value":2},"plot":null,"render_mode":"css","right_units":"screen","top_units":"screen"},"id":"6b5388f9-204b-4f91-91cc-3deb63267fbd","type":"BoxAnnotation"},{"attributes":{"line_alpha":0.1,"line_color":"#1f77b4","line_width":2,"x":{"field":"x"},"y":{"field":"y"}},"id":"edf280c2-162b-4836-95c6-eef0a168e7b6","type":"Line"},{"attributes":{"callback":null,"column_names":["x","y"],"data":{"x":[1,2,3,4,5],"y":[6,7,6,4,5]},"selected":null,"selection_policy":null},"id":"096c9a78-16f6-4f56-a861-d5c0a0fdc967","type":"ColumnDataSource"},{"attributes":{"callback":null},"id":"b6467629-cc28-49f2-97b4-858ec7701a0e","type":"DataRange1d"},{"attributes":{},"id":"85b98586-c5f7-4299-9d9c-90227fd7f25f","type":"PanTool"},{"attributes":{},"id":"13b54b0d-071b-44db-9ea4-7c1bc6d7aafe","type":"WheelZoomTool"},{"attributes":{"overlay":{"id":"6b5388f9-204b-4f91-91cc-3deb63267fbd","type":"BoxAnnotation"}},"id":"e413d83e-8697-4222-8b44-3f7283a67afc","type":"BoxZoomTool"},{"attributes":{},"id":"18afe01f-55f8-4179-8bf3-649becff4c1e","type":"LinearScale"},{"attributes":{},"id":"4fe95fc0-9c0a-4101-9064-d6b423968e17","type":"SaveTool"},{"attributes":{},"id":"782a6afa-ee79-4df9-bb6e-aa29e9c5ac28","type":"ResetTool"},{"attributes":{"callback":null,"column_names":["x","y"],"data":{"x":[1,2,3,4,5],"y":[6,7,6,4,5]},"selected":null,"selection_policy":null},"id":"81260ee0-4f83-4090-80c0-3e4f4e2a6d0d","type":"ColumnDataSource"},{"attributes":{},"id":"b00273c8-1859-42f5-9adb-9fe04e912e09","type":"HelpTool"},{"attributes":{},"id":"402a8433-82fa-49d0-a645-19a789197ec2","type":"BasicTickFormatter"},{"attributes":{"source":{"id":"81260ee0-4f83-4090-80c0-3e4f4e2a6d0d","type":"ColumnDataSource"}},"id":"ea452543-68b8-4b0c-bfc9-660abf79facd","type":"CDSView"},{"attributes":{"fill_color":{"value":"white"},"line_color":{"value":"#1f77b4"},"size":{"units":"screen","value":10},"x":{"field":"x"},"y":{"field":"y"}},"id":"ddb0724b-8e39-44c6-9d84-3dc23fada76c","type":"Circle"},{"attributes":{"fill_alpha":{"value":0.1},"fill_color":{"value":"#1f77b4"},"line_alpha":{"value":0.1},"line_color":{"value":"#1f77b4"},"size":{"units":"screen","value":10},"x":{"field":"x"},"y":{"field":"y"}},"id":"31f846ff-2edd-4e7b-b377-31f9b3297886","type":"Circle"},{"attributes":{"data_source":{"id":"096c9a78-16f6-4f56-a861-d5c0a0fdc967","type":"ColumnDataSource"},"glyph":{"id":"ddb0724b-8e39-44c6-9d84-3dc23fada76c","type":"Circle"},"hover_glyph":null,"muted_glyph":null,"nonselection_glyph":{"id":"31f846ff-2edd-4e7b-b377-31f9b3297886","type":"Circle"},"selection_glyph":null,"view":{"id":"f68f9c52-071d-458a-89d8-2c26d7644061","type":"CDSView"}},"id":"4b0e4132-a10e-403e-9c09-eee59627a869","type":"GlyphRenderer"},{"attributes":{"source":{"id":"096c9a78-16f6-4f56-a861-d5c0a0fdc967","type":"ColumnDataSource"}},"id":"f68f9c52-071d-458a-89d8-2c26d7644061","type":"CDSView"},{"attributes":{},"id":"a4000736-97ab-4f76-9c55-66ed35581caa","type":"LinearScale"},{"attributes":{"callback":null},"id":"7a07edc8-cd10-4f86-9fbb-250af003303a","type":"DataRange1d"},{"attributes":{"formatter":{"id":"2dbd085a-470c-4164-b5ad-53937b02569f","type":"BasicTickFormatter"},"plot":{"id":"bc9b3dad-277d-4218-aeab-7dbead17f708","subtype":"Figure","type":"Plot"},"ticker":{"id":"12e25998-921e-4098-ab04-9d6fe877f2cd","type":"BasicTicker"}},"id":"71730669-4a36-4de6-911a-f3a33e63cc36","type":"LinearAxis"},{"attributes":{"plot":{"id":"bc9b3dad-277d-4218-aeab-7dbead17f708","subtype":"Figure","type":"Plot"},"ticker":{"id":"12e25998-921e-4098-ab04-9d6fe877f2cd","type":"BasicTicker"}},"id":"0765ee2b-22cf-4808-a2f1-7074b0069f9f","type":"Grid"},{"attributes":{"plot":null,"text":"example_bokeh"},"id":"76bdf638-48a1-4c5c-81b1-ce570b82309d","type":"Title"},{"attributes":{},"id":"12e25998-921e-4098-ab04-9d6fe877f2cd","type":"BasicTicker"}],"root_ids":["bc9b3dad-277d-4218-aeab-7dbead17f708"]},"title":"Bokeh Application","version":"0.12.15"}}';
                  var render_items = [{"docid":"c875d55d-486c-4026-9692-ae7fe7379059","elementid":"62c35d67-5a81-482a-8bf7-06c626647e00","modelid":"bc9b3dad-277d-4218-aeab-7dbead17f708"}];
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