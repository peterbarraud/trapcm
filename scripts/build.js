const { log } = require('console');
const fs = require('fs');
const mysql = require('mysql');
// const https = require('http');
const minify = require('html-minifier').minify;

var buildJS = function(){
    console.log('build index.js - Started');
    var b = require('browserify')();
    b.add('src/js/main.js');
    b.transform('uglifyify')
    var indexjs = fs.createWriteStream('build/index.js');
    b.bundle().pipe(indexjs);
    console.log('build index.js - Done!');
};

var buildCSS = function(){
    console.log('build index.css - Started');
    var browserify = require('browserify');
    var fs = require('fs');
    browserify()
    .add('index.js')
    .transform(require('browserify-css'), {
        global:true,
        "minify": true,
        onFlush: function(options, done) {
            fs.appendFileSync('build/index.css', options.data);
            // Do not embed CSS into a JavaScript bundle
            done(null);
        }
    })
    .bundle();    
    console.log('build index.css - Done!');
};





var buildIndexHTML = function(){
    fs.readFile('index.html', 'utf8', (err, htmlString) => {
        console.log('build index.html - Started');
        if (err) {
          console.error(err);
          return;
        }
        // uncomment index.js & index.css
        htmlString = htmlString.replace('<!-- <script src="index.js" name="prod"></script> -->','<script src="index.js"></script>')
        htmlString = htmlString.replace('<!-- <link rel="stylesheet" href="index.css"> -->','<link rel="stylesheet" href="index.css">')
        htmlString = htmlString.replace('<script src="index.js" name="dev"></script>','')
        var lastModified = new Date();
        var lastModified_date_str = lastModified.getDate() + " " +
                                        lastModified.toLocaleString('default', { month: 'long' }) + ", " +
                                        lastModified.getFullYear() + " " +
                                        lastModified.getHours() + ":" + lastModified.getMinutes().toString().padStart(2,"0");
        htmlString = htmlString.replace('[last-modified]',lastModified_date_str);
        var result = minify(htmlString, {
            removeAttributeQuotes: false,
            collapseWhitespace : true,
            collapseInlineTagWhitespace : true,
            removeComments : true
          });
        var indexHtml = fs.createWriteStream('build/index.html');
        indexHtml.write(result);
        indexHtml.close();
        console.log('build index.html - Done!');
    });
};

var buildIncludesHTML = function(){
    let includesDir = './includes/';
    require('mkdirp')('build/includes', function (err) {
        fs.readdir(includesDir, (err, files) => {
            console.log('build includes/*html - Started');
            if (err)
            console.log(err);
            else {
            files.forEach(file => {
                if (file.endsWith(".html")){
                    console.log('build ' + includesDir + file);
                    fs.readFile(includesDir + file, 'utf8', (err, htmlString) => {
                        if (err) {
                        console.error(err);
                        return;
                        }
                        var result = minify(htmlString, {
                            removeAttributeQuotes: false,
                            collapseWhitespace : true,
                            collapseInlineTagWhitespace : true,
                            removeComments : true
                        });
                        var indexHtml = fs.createWriteStream('build/includes/' + file);
                        indexHtml.write(result);
                        indexHtml.close()
                    });                
                    
                }
                console.log('build ' + includesDir + file + " - Done!");
                
            })
            }
            console.log('build includes/*html - Done!');
        })    
    });

}


console.log("using rimraf just to first we clean out the entire build dir");
require('rimraf')('build', function(){
    console.log("re-make the build folder from scratch");
    require('mkdirp')('build', function (err) {
        if (err) {
            console.error(err);
        } else {
            buildJS();
            buildCSS();
            buildIndexHTML();
            buildIncludesHTML();
        }
    });  
});

