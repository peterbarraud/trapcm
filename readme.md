# Browserify with Budo & Bootstrap (using Browserify-CSS)
So going a step on from my [Browserify-CSS template] (https://github.com/peterbarraud/rapo-browserify-budo-browserifycss.git), let's use [browserify-css](https://github.com/cheton/browserify-css) to include [Bootstrap](https://v4-alpha.getbootstrap.com/getting-started/introduction/) in our browserify+budo setup

## What's in this project
* **Bootstrap**: Besides browserify and budo, we're going to include the browserify-css tranform that'll allow us to include the Bootstrap CSS libraries in our project.
* **jQuery**: Bootstrap, requires jQuery so we're going to have to `npm install` that too. But including jQuery is a little more tricky - Take a look at the `index.js`
* **index.js**: Has the references to all your external libs (**CSS** and **JS**). These are the require statements that are browserify'd.
* **./src**: This holds your JS and CSS source files. These are also referenced in `index.js`
* **package.json**: This has a `start` script that runs the localhost. Since we're including Bootstrap, we'll need the `-g` flag for browserify-css. 

## What about Bootstrap with SASS?
Well, you can use the SASS version of Bootstrap, look in the `index.js` for a comment there.

Of course, you're going to have to use a SASS tranform (like maybe SCSSIFY).

Take a look at my [Browserify-SCCIFY](https://github.com/peterbarraud/rapo-browserify-budo-scssify) project for more details.

## Get going
1. Clone this repo
2. `cd` into the resultant dir
3. Run `npm install` to get the dependencies
4. Run `npm start` to launch the project in your default browser running on a local (`Node`-based) web server with `livereload` - all setup.

That's it.

## Building the project for deployment
This is split into two parts
* `build.js`: Builds the `JS` and `CSS` outputs
* `html-dist.config`: Uses [html-dist](https://www.npmjs.com/package/html-dist) to inject the CSS into the HTML

Then generate build:
```
npm run build
```
### Testing the build
If you want to check the build - Just to make sure:
```
npm run testbuild
```
This runs `budo` on the build