var { link } = require('html-dist');

module.exports = {
 // where to write to
 outputFile: './build/index.html',
 // minify the HTML
 minify:true,
 head: {
   // in the <head>, remove any elements matching the 'script' CSS selector
   remove: 'script'
 },
 head: {
   // append the following things to the body
   appends: [
    link({
      rel: 'stylesheet',
      type: 'text/css',
      href: 'index.css'
    })
   ]
 }
}