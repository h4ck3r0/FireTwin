import { NextRequest, NextResponse } from 'next/server';
import { exec } from 'child_process';
import { writeFileSync, mkdirSync, readFileSync } from 'fs';
import { join } from 'path';
import { promisify } from 'util';

const execAsync = promisify(exec);

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData();
    const imageFile = formData.get('image') as File;

    if (!imageFile) {
      return NextResponse.json(
        { error: 'No image provided' },
        { status: 400 }
      );
    }

    // Save the image temporarily
    const tmpDir = join(process.cwd(), 'tmp');
    mkdirSync(tmpDir, { recursive: true });
    
    const imagePath = join(tmpDir, `frame_${Date.now()}.jpg`);
    const imageBuffer = await imageFile.arrayBuffer();
    writeFileSync(imagePath, Buffer.from(imageBuffer));

    // Run Python gauge detector
    const pythonScript = join(
      process.cwd(),
      '..',
      'gauge_reader',
      'detect_from_image.py'
    );

    let result;
    try {
      const { stdout } = await execAsync(
        `cd "${join(process.cwd(), '..', 'gauge_reader')}" && python3 detect_from_image.py "${imagePath}"`,
        { timeout: 10000 }
      );

      result = JSON.parse(stdout);
    } catch (err) {
      result = {
        pressure: 0,
        unit: 'PSI',
        angle_degrees: 0,
        detection_success: false,
        timestamp: Date.now() / 1000
      };
    }

    // Update the gauge_status.json file so the frontend can read it
    const statusFilePath = join(process.cwd(), '..', 'gauge_reader', 'gauge_status.json');
    try {
      const statusData = {
        pressure: result.pressure || 0,
        unit: result.unit || 'PSI',
        gauge_name: result.gauge_name || 'Laptop Camera',
        angle_degrees: result.angle_degrees || 0,
        detection_success: result.detection_success || false,
        timestamp: Date.now() / 1000
      };
      writeFileSync(statusFilePath, JSON.stringify(statusData, null, 2));
    } catch (err) {
      console.error('Could not write status file:', err);
    }
    
    // Clean up temp image
    try {
      const { unlinkSync } = require('fs');
      unlinkSync(imagePath);
    } catch (e) {
      console.error('Failed to delete temp image:', e);
    }
    
    return NextResponse.json(result);
  } catch (error) {
    console.error('Gauge detection error:', error);
    return NextResponse.json(
      { error: 'Detection failed' },
      { status: 500 }
    );
  }
}
