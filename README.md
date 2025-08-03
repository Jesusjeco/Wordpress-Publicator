# WordPress Publicator

A Python desktop application for publishing posts to WordPress with automatic image integration from Shutterstock.

## Features

- **Intuitive GUI**: Clean tkinter interface with 1500x800 window size
- **WordPress Integration**: Secure connection to WordPress REST API
- **Credential Validation**: Test connection before publishing
- **Post Management**: Create posts, save drafts, and publish content
- **Automatic Permalink Generation**: SEO-friendly permalinks from post titles
- **Image Integration**: Automatically add relevant images from multiple sources
- **Content Sanitization**: Automatically removes CSS rules, classes, and data attributes for WordPress compatibility
- **Customizable Image Settings**: Control image frequency and sources
- **Error Handling**: Comprehensive error management and user feedback

## Installation

1. Create virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
# venv\Scripts\activate  # On Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your credentials
```

4. Run the application:
```bash
python main.py
```

## Configuration

### WordPress Setup
1. Enter your WordPress site URL (e.g., https://yoursite.com)
2. Provide your WordPress username and application password
3. Click "Verify Connection" to validate credentials

### Image API Configuration

The application supports multiple image sources. Choose the one that best fits your needs:

#### 🌟 Unsplash API (Recommended)
**High-quality, watermark-free images**

1. **Get Unsplash API credentials:**
   - Visit [Unsplash Developers](https://unsplash.com/developers)
   - Create a free account and application
   - Get your Access Key

2. **Add to your `.env` file:**
   ```
   UNSPLASH_ACCESS_KEY=your_unsplash_access_key_here
   ```

**Benefits:**
- ✅ **No watermarks** on any account type
- ✅ **High-quality** professional photos
- ✅ **Free tier:** 50 requests/hour
- ✅ **Perfect for blogs** and professional content

#### 🔄 Shutterstock API (Alternative)
For users with existing Shutterstock accounts:

1. **Get Shutterstock API credentials:**
   - Visit [Shutterstock Developers](https://www.shutterstock.com/developers)
   - Create an account and application
   - Get your Consumer Key and Secret Key

2. **Add to your `.env` file:**
   ```
   SHUTTERSTOCK_CONSUMER_KEY=your_consumer_key_here
   SHUTTERSTOCK_SECRET_KEY=your_secret_key_here
   ```

**Note:** Free accounts provide watermarked previews. Paid accounts get watermark-free images.

#### 🎨 Placeholder Images (Fallback)
Always available as a fallback option - provides clean, professional placeholder images when other APIs are unavailable.

### Usage Instructions
1. Enable "Add images to post content" in the application
2. Set words per image (default: 200)

## Usage

### Basic Post Creation
1. Enter post title (permalink auto-generates)
2. Write your content in the text area
3. Click "Publish Post" or "Save Draft"

### With Image Integration
When the "Add images to post content" option is enabled:

1. **Choose Image Source**: Select from Unsplash (recommended), Shutterstock, or Placeholder
2. **Automatic Image Insertion**: Images are automatically inserted based on content keywords
3. **Smart Placement**: Images are placed every N words (configurable, default: 200)
4. **Keyword Extraction**: The system extracts relevant keywords from your content
5. **Intelligent Fallback**: If the selected API fails, automatically falls back to placeholder images
6. **Status Updates**: Real-time status updates during image processing

**Image Source Options:**
- **Unsplash**: High-quality, watermark-free professional photos
- **Shutterstock**: Stock photos (watermarked for free accounts)
- **Placeholder**: Clean, professional placeholder images

## Content Processing Features

### Content Sanitization
- **WordPress Compatibility**: Automatically removes CSS rules, classes, and data attributes
- **Clean HTML Output**: Preserves essential HTML structure while removing styling conflicts
- **Allowed Tags**: Maintains safe HTML tags (h1-h6, p, strong, em, ul, ol, li, a, img, br)
- **Attribute Filtering**: Keeps only essential attributes (href, src, alt, title)
- **Always Active**: Content sanitization runs on all posts, regardless of image settings

### Image Processing Features
- **Smart Keyword Extraction**: Analyzes content for relevant terms (up to 6 keywords)
- **Random Image Selection**: Ensures all images are unique with no duplicates
- **Automatic Image Placement**: Inserts images at optimal intervals
- **Content-Aware Selection**: Chooses images matching article topics
- **Paragraph-Aware Insertion**: Images are placed between paragraphs to maintain HTML structure
- **Enhanced Variety**: Fetches 10 images per search and randomly selects from available options
- **Duplicate Prevention**: Tracks used images and prevents repetition within the same post
- **WordPress Media Library Integration**: Upload images directly to your WordPress Media Library
- **Fallback Handling**: Continues without images if API fails
- **Preview URLs**: Uses appropriate image sources based on API availability

### WordPress Media Library Upload
When enabled, images are uploaded directly to your WordPress Media Library instead of using external URLs:

**Benefits:**
- ✅ **Direct Management**: Images appear in your WordPress Media Library
- ✅ **Reusable Assets**: Use uploaded images in future posts
- ✅ **Editor Integration**: Images are available in the WordPress editor
- ✅ **Better Performance**: Images are served from your WordPress site
- ✅ **Backup Included**: Images are included in WordPress backups
- ✅ **SEO Friendly**: Images use your domain for better SEO

**How to Enable:**
1. Enable "Add images to post content"
2. Check "Upload to WordPress Media Library"
3. Images will be automatically uploaded and embedded using WordPress URLs

**Note:** This feature requires a valid WordPress connection and may take slightly longer due to upload processing.

## Requirements

- Python 3.7+
- WordPress site with REST API enabled
- Valid WordPress credentials
- Shutterstock API credentials (optional, for image integration)

## File Structure

```
wordpress-publicator/
├── main.py              # Main GUI application
├── wordpress_api.py     # WordPress REST API integration
├── image_api.py         # Shutterstock API integration
├── requirements.txt     # Python dependencies
├── .env.example        # Environment variables template
└── README.md           # Documentation
```