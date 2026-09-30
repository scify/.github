// Copies src/ to dist/ so that the CI build job has something to build.
import { cpSync, rmSync } from 'node:fs';

rmSync('dist', { recursive: true, force: true });
cpSync('src', 'dist', { recursive: true });
console.log('Built dist/');
