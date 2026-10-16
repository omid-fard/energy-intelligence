# آموزش انتشار Energy Intelligence روی GitHub — فقط با مرورگر

هیچ نیازی به نصب Python، Docker یا IDE روی مک ندارید. این بسته **یک مخزن با همه امکانات** است. GitHub Actions روی سرورهای GitHub کد Python را اجرا می‌کند و سایت را با GitHub Pages منتشر می‌کند.

## ۱. ساخت مخزن عمومی

1. فایل ZIP را دانلود کنید و در Finder دوبار کلیک کنید.
2. وارد https://github.com/new شوید.
3. نام `energy-intelligence`، توضیح زیر و گزینه `Public` را وارد کنید:
   `German electricity market intelligence: real SMARD data, negative prices, renewable energy analytics, transparent ML forecasting, Python and GitHub Pages.`
4. گزینه Add README را فعال نکنید. مخزن را با دکمه Create repository بسازید.

## ۲. آپلود فایل‌ها، نه ZIP

1. در مخزن روی `uploading an existing file` یا `Add file → Upload files` کلیک کنید.
2. پوشه استخراج‌شده را در Finder باز کنید؛ برای نمایش `.github` پنهان از `Command + Shift + .` استفاده کنید.
3. محتویات **داخل** پوشه را همگی انتخاب کنید (نباید یک پوشه تودرتوی اضافی در ریشه مخزن ساخته شود).
4. آن‌ها را در صفحه آپلود رها کنید و در پایین صفحه روی `Commit changes` بزنید.
5. مطمئن شوید فایل `.github/workflows/publish.yml` در ریشه مخزن وجود دارد.

## ۳. فعال‌سازی سایت

1. از `Settings → Pages`، بخش Build and deployment را باز کنید.
2. گزینه `Source` را روی `GitHub Actions` قرار دهید.
3. تب `Actions` را باز کنید و گردش‌کار `Energy Intelligence - Refresh & Publish` را اجرا کنید: `Run workflow`.
4. **منتظر تیک سبز** و خروجی صحیح باشید. اگر قرمز است، خروجی log مرحله SMARD را بررسی و تصویر خطا را ارسال کنید.
5. پس از موفقیت، از Settings → Pages آدرس واقعی را بردارید، مانند `https://YOUR-USERNAME.github.io/energy-intelligence/`.
6. سایت را باز کنید. آیا در بالا داده‌ها با زمان و منطقه درست نشان داده می‌شوند؟ آیا نمودار قیمت و اطلاعات واقعی بارگذاری می‌شوند؟

## ۴. تنظیمات دیده‌شدن GitHub

1. در صفحه اصلی مخزن، بخش `About` و آیکون چرخ‌دنده را پیدا کنید.
2. Description را از مرحله ۱ حفظ کنید و URL سایت را در `Website` وارد کنید.
3. در قسمت `Topics` کلمات بدون هشتگ از فایل `GITHUB_LINKEDIN_KEYWORDS.md` را یکی‌یکی اضافه و Save کنید.
4. اگر می‌خواهید پروژه در صفحه پروفایل شخصی GitHub نیز دیده شود، از صفحه پروفایل بخش Customize your pins را برای پین کردن همین مخزن استفاده کنید.

## ۵. معرفی در LinkedIn — فقط بعد از تأیید

1. صفحه شرکت Hope Intelligence را به‌عنوان admin باز کنید.
2. بخش About را با معرفی انگلیسی/آلمانی موجود در `GITHUB_LINKEDIN_KEYWORDS.md` تقویت کنید.
3. آدرس سایت واقعی را در Website بگذارید.
4. از متن‌های فایل `LINKEDIN_LAUNCH_COPY.md` برای پست اولیه استفاده کنید، جای خالی لینک‌ها را با آدرس واقعی سایت و GitHub پر کنید و یک تصویر از نمودار **واقعی** اضافه کنید.
5. بعد از انتشار، آمار بازدید، کلیک، جست‌وجو و تعامل مخاطبان صنعت انرژی را بسنجید.

### هشدارهای دقیق

- عددهای واقعی هنوز در این ZIP نیستند؛ `docs/data/dashboard.json` عمداً خالی است. صرف آپلود، موفقیت پروژه را اثبات نمی‌کند.
- در صورت قطع SMARD یا اشتباه API، اجرای Actions ممکن است شکست بخورد؛ نمودار ساختگی ساخته نمی‌شود.
- پیش‌بینی پژوهشی است و صرفه‌جویی صنعتی تضمین‌شده ارائه نمی‌دهد.
- وب‌سایت static است، سرور Python دائمی و PostgreSQL یا FastAPI ندارد.
- نام کاربری یا URL واقعی شما هنوز در اسناد وجود ندارد؛ جایگزین کردن آن پس از انتشار ضروری است.
