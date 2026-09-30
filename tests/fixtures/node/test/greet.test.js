import assert from 'node:assert/strict';
import test from 'node:test';

import { greet } from '../src/greet.js';

test('greet returns a greeting', () => {
    assert.equal(greet('SciFY'), 'Hello, SciFY!');
});
