"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.onStoryDown = onStoryDown;
function onStoryDown(cleanFn) {
    var storyRoot = document.getElementById("storybook-root");
    if (storyRoot) {
        // Create an observer instance linked to the callback function
        var observer = new MutationObserver(function (_records, observer) {
            cleanFn();
            observer.disconnect();
        });
        // Start observing the target node for configured mutations
        observer.observe(storyRoot, { childList: true });
    }
}
