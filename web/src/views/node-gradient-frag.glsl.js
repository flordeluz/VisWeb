"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
// language=GLSL
var SHADER_SOURCE = /*glsl*/ "\nprecision mediump float;\n\nvarying vec4 v_color;\nvarying float v_border;\n\nconst float radius = 0.5;\nconst float halfRadius = 0.35;\n\nvoid main(void) {\n  vec4 transparent = vec4(0.0, 0.0, 0.0, 0.0);\n  vec4 white = vec4(1.0, 1.0, 1.0, 1.0);\n  float distToCenter = length(gl_PointCoord - vec2(0.5, 0.5));\n\n  #ifdef PICKING_MODE\n  if (distToCenter < radius)\n    gl_FragColor = v_color;\n  else\n    gl_FragColor = transparent;\n  #else\n  // For normal mode, we use the color:\n  if (distToCenter > radius)\n    gl_FragColor = transparent;\n  else if (distToCenter > radius - v_border)\n    gl_FragColor = mix(transparent, v_color, (radius - distToCenter) / v_border);\n  else\n    gl_FragColor = mix(v_color, white, (radius - distToCenter) / radius);\n  #endif\n}\n";
exports.default = SHADER_SOURCE;
