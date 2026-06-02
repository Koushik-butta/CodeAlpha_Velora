# Velora — Premium Tricolor Indian Marketplace

Velora is a state-of-the-art e-commerce and barter marketplace designed specifically for the Indian community. It blends the best features of OLX, Amazon, and Flipkart into a unified platform styled around a sleek, modern visual aesthetic. Users can **Buy**, **Sell**, or **Exchange (Swap)** products across India with real-time interactive dashboards, multi-theme personalization, and high-performance UI micro-interactions.

---

## 🌟 Key Features

### 🎨 Premium UI & Multi-Theme Customization
* **Tricolor Identity**: A patriotic-inspired color palette (Saffron Orange, White, Emerald Green, and Navy Blue) honoring the Indian marketplace.
* **14-Theme Engine**: Real-time theme customization engine featuring premium styles like *Sakura Blossom*, *Cosmic Lavender*, *Nordic Aurora*, and *Desert Amber*.
* **Circular Theme sweep**: Switching themes fires a circular ripple transition centered directly on your cursor.
* **Ambient Animation Effects**:
  * 3D card tilt and mouse-tracking radial gradient spotlights on product cards.
  * Interactive canvas particle burst sparks on logo clicks and review star ratings.
  * Soft, blurry ambient gradient floating blobs drifting in the landing page background.
  * Fading cursor particle trails following mouse movements.
  * Full-screen SVG confetti shower physics on successful checkouts.

### ⚡ E-Commerce & Checkout Capabilities
* **Slide-over Cart Drawer**: Sleek slide-out panel from the screen edge with an AJAX-based real-time quantity modifier. Updates trigger badge-spring scaling animations on the header.
* **"Buy Now" (Direct Checkout)**: Bypass the shopping cart entirely to order products instantly.
* **Auto-inventory Sold States**: Purchased items are immediately marked as sold, preventing duplicate checkouts. Cancelled orders automatically restore inventory globally.

### 🔄 Barter Swap Platform
* **Interactive Exchange Portal**: Request barter swaps by offering one of your items for another seller's listing.
* **Energy Line SVG Pulse**: Active exchange details showcase requester and receiver items linked by a glowing green vector connection path with animating dashed lines.

### 📝 Step-by-Step Selling Wizard
* **5-Step Form Stepper**: Organized panels split into step groups: *Details, Pricing, Location, Photo Upload, and Review*.
* **Publish vs. Save Draft**:
  * **Save Draft**: Saves listings as inactive drafts (`is_active=False`) and redirects to a dedicated draft manager. Sellers can preview their inactive drafts privately on detail pages, while other buyers see a 404 page.
  * **Publish Listing**: Direct activation (`is_active=True`) rendering instantly in search and categories.
* **Cloudinary Storage**: High-performance CDN hosting with direct FileReader previews for selected images.

### 🔍 Live Search Autocomplete
* **Debounced Suggestions**: Dynamic autocomplete dropdown suggesting active unsold products as you type (starting from the very first letter).
* **Comprehensive Search Filter**: Scan keywords in *Title, Brand, Model Name, City, State, Description, and Category*. Includes sorting options and category filter pills.

### 🛡️ Administrative & Seller Control
* **Owner Bypass for `b.kowshik2007@gmail.com`**: Auto-promoted superuser permissions allow managing, editing, or deleting any user's product globally.
* **Seller Sales Tracker**: Detailed order tracking log showing buyer coordinates (Name, Email, Phone) and shipping address snapshots.
* **Seller Cancellation Control**: Sellers can cancel active orders on their products, returning items to the global pool instantly.

---

## 🛠️ Technology Stack

* **Backend**: Django 5.x (Python 3.13)
* **Database**: PostgreSQL (Production/Neon serverless) / SQLite (Local Dev)
* **Frontend**: Vanilla HTML5, CSS Custom Variables (HSL Hue Tokens), Javascript (ES6)
* **Media Storage**: Cloudinary Image Hosting
* **Email Gateway**: Brevo Integration

---

## 🚀 Installation & Local Setup

### 1. Clone the repository
```bash
git clone https://github.com/Koushik-butta/CodeAlpha_Velora.git
cd CodeAlpha_Velora
```

### 2. Set up virtual environment
```bash
python -m venv venv
venv\Scripts\activate   # On Windows
source venv/bin/activate # On macOS/Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Variables (`.env`)
Create a `.env` file in the root directory:
```env
SECRET_KEY=your-django-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
USE_SQLITE_DEV=True  # Set False to use Neon PostgreSQL

# Cloudinary Integration
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret

# Brevo Integration (Optional)
BREVO_API_KEY=your_brevo_api_key
BREVO_SENDER_EMAIL=noreply@example.com
BREVO_SENDER_NAME=Velora
```

### 5. Run migrations & Seed
```bash
python manage.py migrate
```

### 6. Start development server
```bash
python manage.py runserver
```
Visit the local server at `http://127.0.0.1:8000/`.

---

## 🧪 Running Tests
Verify your environment settings and routing using the integrated test suite:
```bash
python manage.py test
```
