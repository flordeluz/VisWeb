"use strict";
var __extends = (this && this.__extends) || (function () {
    var extendStatics = function (d, b) {
        extendStatics = Object.setPrototypeOf ||
            ({ __proto__: [] } instanceof Array && function (d, b) { d.__proto__ = b; }) ||
            function (d, b) { for (var p in b) if (Object.prototype.hasOwnProperty.call(b, p)) d[p] = b[p]; };
        return extendStatics(d, b);
    };
    return function (d, b) {
        if (typeof b !== "function" && b !== null)
            throw new TypeError("Class extends value " + String(b) + " is not a constructor or null");
        extendStatics(d, b);
        function __() { this.constructor = d; }
        d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
var rendering_1 = require("sigma/rendering");
var utils_1 = require("sigma/utils");
var node_gradient_frag_glsl_1 = require("./node-gradient-frag.glsl");
var node_gradient_vert_glsl_1 = require("./node-gradient-vert.glsl");
var UNSIGNED_BYTE = WebGLRenderingContext.UNSIGNED_BYTE, FLOAT = WebGLRenderingContext.FLOAT;
var UNIFORMS = ["u_sizeRatio", "u_pixelRatio", "u_matrix"];
var NodeGradientProgram = /** @class */ (function (_super) {
    __extends(NodeGradientProgram, _super);
    function NodeGradientProgram() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    NodeGradientProgram.prototype.getDefinition = function () {
        return {
            VERTICES: 1,
            VERTEX_SHADER_SOURCE: node_gradient_vert_glsl_1.default,
            FRAGMENT_SHADER_SOURCE: node_gradient_frag_glsl_1.default,
            METHOD: WebGLRenderingContext.POINTS,
            UNIFORMS: UNIFORMS,
            ATTRIBUTES: [
                { name: "a_position", size: 2, type: FLOAT },
                { name: "a_size", size: 1, type: FLOAT },
                { name: "a_color", size: 4, type: UNSIGNED_BYTE, normalized: true },
                { name: "a_id", size: 4, type: UNSIGNED_BYTE, normalized: true },
            ],
        };
    };
    NodeGradientProgram.prototype.processVisibleItem = function (nodeIndex, startIndex, data) {
        var array = this.array;
        array[startIndex++] = data.x;
        array[startIndex++] = data.y;
        array[startIndex++] = data.size;
        array[startIndex++] = (0, utils_1.floatColor)(data.color);
        array[startIndex++] = nodeIndex;
    };
    NodeGradientProgram.prototype.setUniforms = function (params, _a) {
        var gl = _a.gl, uniformLocations = _a.uniformLocations;
        var u_sizeRatio = uniformLocations.u_sizeRatio, u_pixelRatio = uniformLocations.u_pixelRatio, u_matrix = uniformLocations.u_matrix;
        gl.uniform1f(u_sizeRatio, params.sizeRatio);
        gl.uniform1f(u_pixelRatio, params.pixelRatio);
        gl.uniformMatrix3fv(u_matrix, false, params.matrix);
    };
    return NodeGradientProgram;
}(rendering_1.NodeProgram));
exports.default = NodeGradientProgram;
