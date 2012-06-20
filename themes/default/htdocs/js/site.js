/**
 * This file contains site/theme specific javascript definitions.
 */

/**
 * Returns color based on given number
 * @param {Integer} seed
 * @example
 *
 * selectColor(123):
 * '#ff00ff'
 * selectColor(123):
 * '#ff00ff'
 * selectColor(201):
 * '#edff00'
 *
 */
var getColor = function(seed) {
    var colors = [
        '#264581',
        '#5b7e36',
        '#d75330',
        '#eae83f',
        '#d78630',
        '#a41c1c',
        '#c41c53',
        '#ab2ba0',
        '#672d98',
        '#2d8398'
    ];
    return colors[seed % colors.length];
};

// Global variables
theme = {
    contentWidth:776,
    fillColor:'#365594',
    fontFamily:'Tahoma',
    fontSize:12,
    getColor:getColor
};


