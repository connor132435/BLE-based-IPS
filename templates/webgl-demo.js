// Define the function to make the AJAX request
function makeRequest(url, method, data, callback) {
    var xhr = new XMLHttpRequest();

    // Set up the callback function to handle the response
    xhr.onreadystatechange = function() {
        if (xhr.readyState === 4) { // Request is complete
            if (xhr.status >= 200 && xhr.status < 300) { // Successful response
                callback(null, xhr.responseText);
            } else { // Error in response
                callback(xhr.status);
            }
        }
    };

    // Open the request
    xhr.open(method, url, true);

    // Set the content type for POST requests
    if (method === 'POST' && data) {
        xhr.setRequestHeader('Content-Type', 'application/json');
    }

    // Send the request
    if (data) {
        xhr.send(JSON.stringify(data));
    } else {
        xhr.send();
    }
}


const canvas = document.getElementById('webgl-canvas');
const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');

if (!gl) {
    alert('WebGL not supported, falling back on experimental-webgl');
}
if (!gl) {
    alert('Your browser does not support WebGL');
}

// Vertex shader program
const vertexShaderSource = `
    attribute vec4 a_position;
    attribute vec4 a_color;
    uniform mat4 u_matrix;
    varying vec4 v_color;
    void main() {
        gl_Position = u_matrix * a_position;
        v_color = a_color;
    }
`;

// Fragment shader program
const fragmentShaderSource = `
    precision mediump float;
    varying vec4 v_color;
    void main() {
        gl_FragColor = v_color;
    }
`;

function createShader(gl, type, source) {
    const shader = gl.createShader(type);
    gl.shaderSource(shader, source);
    gl.compileShader(shader);
    if (gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
        return shader;
    }
    console.log(gl.getShaderInfoLog(shader));
    gl.deleteShader(shader);
}

const vertexShader = createShader(gl, gl.VERTEX_SHADER, vertexShaderSource);
const fragmentShader = createShader(gl, gl.FRAGMENT_SHADER, fragmentShaderSource);

function createProgram(gl, vertexShader, fragmentShader) {
    const program = gl.createProgram();
    gl.attachShader(program, vertexShader);
    gl.attachShader(program, fragmentShader);
    gl.linkProgram(program);
    if (gl.getProgramParameter(program, gl.LINK_STATUS)) {
        return program;
    }
    console.log(gl.getProgramInfoLog(program));
    gl.deleteProgram(program);
}

const program = createProgram(gl, vertexShader, fragmentShader);

function createBox() {
    const positions = new Float32Array([
        // Front face
        -1.0, -1.0,  0.615, // Vertex 1
         1.0, -1.0,  0.615, // Vertex 2
         1.0,  1.0,  0.615, // Vertex 3
         0.45, 1.0,  0.615, // Vertex 4
         0.45, 0.532,  0.615, // Vertex 5
        -1.0,  0.532,  0.615, // Vertex 6

        // Back face
        -1.0, -1.0, -0.615, // Vertex 7
         1.0, -1.0, -0.615, // Vertex 8
         1.0,  1.0, -0.615, // Vertex 9
         0.45, 1.0,  -0.615, // Vertex 10
         0.45, 0.532,  -0.615, // Vertex 11
        -1.0,  0.532, -0.615, // Vertex 12
    ]);

    const colors = new Float32Array([
        // Colors for each vertex (white for all)
        1.0,  1.0,  1.0,  1.0, // white
        1.0,  1.0,  1.0,  1.0, // white
        1.0,  1.0,  1.0,  1.0, // white
        1.0,  1.0,  1.0,  1.0, // white
        1.0,  1.0,  1.0,  1.0, // white
        1.0,  1.0,  1.0,  1.0, // white
        1.0,  1.0,  1.0,  1.0, // white
        1.0,  1.0,  1.0,  1.0, // white
        1.0,  1.0,  1.0,  1.0, // white
        1.0,  1.0,  1.0,  1.0, // white
        1.0,  1.0,  1.0,  1.0, // white
        1.0,  1.0,  1.0,  1.0, // white
    ]);

    const indices = new Uint16Array([
        // Front face edges
        0, 1, // Bottom edge
        1, 2, // Right edge
        2, 3, // Top edge
        3, 4, // Left edge
        4, 5,
        5, 0,

        // Back face edges
        6, 7, // Bottom edge
        7, 8, // Right edge
        8, 9, // Top edge
        9, 10, // Left edge
        10, 11,
        11, 6,

        // Connecting edges
        0, 6, // Bottom left edge
        1, 7, // Bottom right edge
        2, 8, // Top right edge
        3, 9, // Top left edge
        4, 10,
        5, 11,
    ]);

    return { positions, colors, indices };
}

function createSphere(radius, slices, stacks, centerX, centerY, centerZ, color) {
    const positions = [];
    const colors = [];
    const indices = [];

    for (let stack = 0; stack <= stacks; ++stack) {
        const phi = stack * Math.PI / stacks;
        const sinPhi = Math.sin(phi);
        const cosPhi = Math.cos(phi);

        for (let slice = 0; slice <= slices; ++slice) {
            const theta = slice * 2 * Math.PI / slices;
            const sinTheta = Math.sin(theta);
            const cosTheta = Math.cos(theta);

            const x = radius * cosTheta * sinPhi;
            const y = radius * cosPhi;
            const z = radius * sinTheta * sinPhi;

            positions.push(x + centerX, y + centerY, z + centerZ);
            colors.push(...color);
        }
    }

    for (let stack = 0; stack < stacks; ++stack) {
        for (let slice = 0; slice < slices; ++slice) {
            const first = (stack * (slices + 1)) + slice;
            const second = first + slices + 1;

            indices.push(first, second, first + 1);
            indices.push(second, second + 1, first + 1);
        }
    }

    return { positions, colors, indices };
}

const raspcolor = [0.886, 0.0429, 0.359, 1.0];
const boxData = createBox();
const sphereData = createSphere(0.02, 32, 32, 0.91, -0.91, 0.333, raspcolor);

const boxPositionBuffer = gl.createBuffer();
gl.bindBuffer(gl.ARRAY_BUFFER, boxPositionBuffer);
gl.bufferData(gl.ARRAY_BUFFER, boxData.positions, gl.STATIC_DRAW);

const boxColorBuffer = gl.createBuffer();
gl.bindBuffer(gl.ARRAY_BUFFER, boxColorBuffer);
gl.bufferData(gl.ARRAY_BUFFER, boxData.colors, gl.STATIC_DRAW);

const boxIndexBuffer = gl.createBuffer();
gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, boxIndexBuffer);
gl.bufferData(gl.ELEMENT_ARRAY_BUFFER, boxData.indices, gl.STATIC_DRAW);

const spherePositionBuffer = gl.createBuffer();
gl.bindBuffer(gl.ARRAY_BUFFER, spherePositionBuffer);
gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(sphereData.positions), gl.STATIC_DRAW);

const sphereColorBuffer = gl.createBuffer();
gl.bindBuffer(gl.ARRAY_BUFFER, sphereColorBuffer);
gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(sphereData.colors), gl.STATIC_DRAW);

const sphereIndexBuffer = gl.createBuffer();
gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, sphereIndexBuffer);
gl.bufferData(gl.ELEMENT_ARRAY_BUFFER, new Uint16Array(sphereData.indices), gl.STATIC_DRAW);

const positionAttributeLocation = gl.getAttribLocation(program, "a_position");
const colorAttributeLocation = gl.getAttribLocation(program, "a_color");
const matrixUniformLocation = gl.getUniformLocation(program, "u_matrix");

gl.enableVertexAttribArray(positionAttributeLocation);
gl.bindBuffer(gl.ARRAY_BUFFER, boxPositionBuffer);
gl.vertexAttribPointer(positionAttributeLocation, 3, gl.FLOAT, false, 0, 0);

gl.enableVertexAttribArray(colorAttributeLocation);
gl.bindBuffer(gl.ARRAY_BUFFER, boxColorBuffer);
gl.vertexAttribPointer(colorAttributeLocation, 4, gl.FLOAT, false, 0, 0);

const fieldOfViewRadians = Math.PI / 4;
const aspect = canvas.clientWidth / canvas.clientHeight;
const zNear = 0.1;
const zFar = 100.0;
const projectionMatrix = mat4.create();
mat4.perspective(projectionMatrix, fieldOfViewRadians, aspect, zNear, zFar);

const cameraPosition = [0, 0, -4];
const up = [0, 1, 0];
const target = [0, 0, 0];
const cameraMatrix = mat4.create();
mat4.lookAt(cameraMatrix, cameraPosition, target, up);

const viewMatrix = mat4.create();
mat4.invert(viewMatrix, cameraMatrix);

const viewProjectionMatrix = mat4.create();
mat4.multiply(viewProjectionMatrix, projectionMatrix, viewMatrix);

const worldMatrix = mat4.create();
const worldViewProjectionMatrix = mat4.create();

let isDragging = false;
let lastX = 0;
let lastY = 0;
let rotationX = 0;
let rotationY = 0;
let distance = 4.0;

canvas.addEventListener('mousedown', (event) => {
    isDragging = true;
    lastX = event.clientX;
    lastY = event.clientY;
});

canvas.addEventListener('mouseup', () => {
    isDragging = false;
});

canvas.addEventListener('mousemove', (event) => {
    if (isDragging) {
        const deltaX = event.clientX - lastX;
        const deltaY = event.clientY - lastY;
        rotationX += deltaY * 0.01;
        rotationY += deltaX * 0.01;
        lastX = event.clientX;
        lastY = event.clientY;
    }
});

canvas.addEventListener('wheel', (event) => {
    const zoomSpeed = 0.001;
    distance += event.deltaY * zoomSpeed;
    //distance = Math.max(1.0, Math.min(10.0, distance));  // Clamp the distance
});

function drawScene() {
    mat4.identity(worldMatrix);
    mat4.translate(worldMatrix, worldMatrix, [0, 0, -distance]);
    mat4.rotate(worldMatrix, worldMatrix, rotationX, [1, 0, 0]);
    mat4.rotate(worldMatrix, worldMatrix, rotationY, [0, 1, 0]);
    mat4.multiply(worldViewProjectionMatrix, viewProjectionMatrix, worldMatrix);

    gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);
    gl.useProgram(program);
    gl.uniformMatrix4fv(matrixUniformLocation, false, worldViewProjectionMatrix);

    gl.bindBuffer(gl.ARRAY_BUFFER, boxPositionBuffer);
    gl.vertexAttribPointer(positionAttributeLocation, 3, gl.FLOAT, false, 0, 0);
    gl.bindBuffer(gl.ARRAY_BUFFER, boxColorBuffer);
    gl.vertexAttribPointer(colorAttributeLocation, 4, gl.FLOAT, false, 0, 0);
    gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, boxIndexBuffer);
    gl.drawElements(gl.LINES, boxData.indices.length, gl.UNSIGNED_SHORT, 0);

    gl.bindBuffer(gl.ARRAY_BUFFER, spherePositionBuffer);
    gl.vertexAttribPointer(positionAttributeLocation, 3, gl.FLOAT, false, 0, 0);
    gl.bindBuffer(gl.ARRAY_BUFFER, sphereColorBuffer);
    gl.vertexAttribPointer(colorAttributeLocation, 4, gl.FLOAT, false, 0, 0);
    gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, sphereIndexBuffer);
    gl.drawElements(gl.TRIANGLES, sphereData.indices.length, gl.UNSIGNED_SHORT, 0);

    requestAnimationFrame(drawScene);
}

gl.clearColor(0, 0, 0, 1);
gl.enable(gl.DEPTH_TEST);

requestAnimationFrame(drawScene);


// Example usage of the makeRequest function
var url = 'localhost:8080/getData';
var method = 'GET'; // Can be 'GET' or 'POST'
var data = null; // Data to send with POST requests

function parse(response){
    return response;
}

makeRequest(url, method, data, function(error, response) {
    if (error) {
        console.error('Error:', error);
        return;
    }
    response = parse(response);
    const sphereData2 = createSphere(0.02, 32, 32, 0.91, -0.91, 0.333, raspcolor);
});

