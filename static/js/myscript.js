function removeURLParametr(url, parametr) {
    var urlparts = url.split('?');
    if (urlparts.length >= 2) {
        var prefix = encodeURIComponent(parametr) + '=';
        var pars = urlparts[1].split(/[&;]/g);
        for (var i = pars.length; i-- > 0;) {
            if (pars[i].lastIndexOf(prefix, 0) !== -1) {
                pars.splice(i, 1);
            }
        }
        return urlparts[0] + (pars.length > 0 ? '?' + pars.join('&') : '');
    }
    return url;
}

function select_sort() {
    var select_sort_value = $("#select_sort").val();
    var url = removeURLParametr(window.location.href, "sort_type");
    if (url.includes('?')) {
        window.location = url + "&sort_type=" + select_sort_value;
    } else {
        window.location = url + "?sort_type=" + select_sort_value;
    }
}

function updateFilterCounts() {
    $('.widget-filters__item').each(function() {
        var filterSection = $(this);
        filterSection.find('.filter__title').each(function() {
            var titleButton = $(this);
            var filterContainer = titleButton.closest('.card, .filter');
            var checkedCount = filterContainer.find('.input-check__input:checked').length;

            titleButton.find('.filter-count').remove();
            if (checkedCount > 0) {
                titleButton.append(' <span class="filter-count">' + checkedCount + '</span>');
            }
        });
    });
}

$(document).ready(function() {
    updateFilterCounts();

    var urlParams = new URLSearchParams(window.location.search);
    urlParams.delete('page');
    if (urlParams.toString() !== "") {
        $('#reset_filters_btn').css('display', 'inline-block');
    }

    var favorites = JSON.parse(localStorage.getItem('favorites'));
    if (favorites) {
        favorites.forEach(function(fav) {
            var element = $('#' + fav.id);
            if (element.length) {
                element.prop('checked', fav.value);
            }
        });
        updateFilterCounts();
    }

    var priceSliderElement = document.getElementById('price-slider');
    if (priceSliderElement) {
        var minPrice = parseInt(priceSliderElement.getAttribute('data-min'));
        var maxPrice = parseInt(priceSliderElement.getAttribute('data-max'));
        var startMin = parseInt(urlParams.get('price_min')) || minPrice;
        var startMax = parseInt(urlParams.get('price_max')) || maxPrice;

        noUiSlider.create(priceSliderElement, {
            start: [startMin, startMax],
            connect: true,
            step: 100000,
            range: { 'min': minPrice, 'max': maxPrice },
            format: {
                to: function(value) { return Math.round(value).toLocaleString(); },
                from: function(value) { return Number(value.replace(/,/g, '')); }
            }
        });

        var minDisplay = document.getElementById('price-min-display');
        var maxDisplay = document.getElementById('price-max-display');
        var minHidden = document.getElementById('price_min_hidden');
        var maxHidden = document.getElementById('price_max_hidden');

        priceSliderElement.noUiSlider.on('update', function(values, handle) {
            var plainValue = Number(values[handle].replace(/,/g, ''));
            if (handle === 0) {
                minDisplay.innerHTML = values[handle];
                minHidden.value = plainValue;
            } else {
                maxDisplay.innerHTML = values[handle];
                maxHidden.value = plainValue;
            }
        });
    }

    $('#select_sort').on('change', select_sort);
    
    $('#reset_filters_btn').on('click', function() {
        localStorage.removeItem('favorites');
    });

    $('input:checkbox.input-check__input').on('change', function() {
        updateFilterCounts();
        var favs = [];
        $('input:checkbox.input-check__input').each(function() {
            favs.push({ id: $(this).attr('id'), value: $(this).prop('checked') });
        });
        localStorage.setItem("favorites", JSON.stringify(favs));
    });
});





































// function removeURLParametr(url, parametr) {
//     var urlparts = url.split('?');
//     if (urlparts.length >= 2) {
//         var prefix = encodeURIComponent(parametr) + '=';
//         var pars = urlparts[1].split(/[&;]/g);
//         for (var i = pars.length; i-- > 0;) {
//             if (pars[i].lastIndexOf(prefix, 0) !== -1) {
//                 pars.splice(i, 1);
//             }
//         }
//         return urlparts[0] + (pars.length > 0 ? '?' + pars.join('&') : '');
//     }
//     return url;
// }

// function select_sort() {
//     var select_sort_value = $("#select_sort").val();
//     var url = removeURLParametr(window.location.href, "sort_type");
//     if (url.includes('?')) {
//         window.location = url + "&sort_type=" + select_sort_value;
//     } else {
//         window.location = url + "?sort_type=" + select_sort_value;
//     }
// }

// function updateFilterCounts() {
//     // برای هر بخش فیلتر به صورت مجزا اجرا می‌شود
//     $('.widget-filters__item').each(function() {
//         var filterSection = $(this);
//         // تمام عنوان‌های داخل این بخش را پیدا می‌کند (برای بخش ویژگی‌ها مهم است)
//         filterSection.find('.filter__title').each(function() {
//             var titleButton = $(this);
//             // ظرف اصلی هر زیر-بخش را پیدا می‌کند
//             var filterContainer = titleButton.closest('.card, .filter'); 
//             var checkedCount = filterContainer.find('.input-check__input:checked').length;
            
//             titleButton.find('.filter-count').remove();
//             if (checkedCount > 0) {
//                 titleButton.append(' <span class="filter-count">' + checkedCount + '</span>');
//             }
//         });
//     });
// }

// $(document).ready(function() {
//     console.log("Document is ready. Initializing scripts.");

//     // --- راه‌اندازی اولیه ---
//     updateFilterCounts();

//     var urlParams = new URLSearchParams(window.location.search);
//     urlParams.delete('page');
//     if (urlParams.toString() !== "") {
//         $('#reset_filters_btn').css('display', 'inline-block');
//     }
//     // این کد را داخل $(document).ready(...) قرار دهید

//         // رویداد کلیک برای دکمه حذف فیلترها
//         $('#reset_filters_btn').on('click', function() {
//             // با کلیک روی این دکمه، حافظه مربوط به چک‌باکس‌ها را پاک کن
//             localStorage.removeItem('favorites');
//         });

//     var favorites = JSON.parse(localStorage.getItem('favorites'));
//     if (favorites) {
//         favorites.forEach(function(fav) {
//             var element = $('#' + fav.id);
//             if (element.length) {
//                 element.prop('checked', fav.value);
//             }
//         });
//         updateFilterCounts(); 
//     }

//     // --- اسلایدر قیمت ---
//     var priceSliderElement = document.getElementById('price-slider');
//     if (priceSliderElement) {
//         var minPrice = parseInt(priceSliderElement.getAttribute('data-min'));
//         var maxPrice = parseInt(priceSliderElement.getAttribute('data-max'));
//         var startMin = parseInt(urlParams.get('price_min')) || minPrice;
//         var startMax = parseInt(urlParams.get('price_max')) || maxPrice;

//         noUiSlider.create(priceSliderElement, {
//             start: [startMin, startMax],
//             connect: true,
//             step: 100000,
//             range: { 'min': minPrice, 'max': maxPrice },
//             format: {
//                 to: function(value) { return Math.round(value).toLocaleString(); },
//                 from: function(value) { return Number(value.replace(/,/g, '')); }
//             }
//         });

//         var minDisplay = document.getElementById('price-min-display');
//         var maxDisplay = document.getElementById('price-max-display');
//         var minHidden = document.getElementById('price_min_hidden');
//         var maxHidden = document.getElementById('price_max_hidden');

//         priceSliderElement.noUiSlider.on('update', function(values, handle) {
//             var plainValue = Number(values[handle].replace(/,/g, ''));
//             if (handle === 0) {
//                 minDisplay.innerHTML = values[handle];
//                 minHidden.value = plainValue;
//             } else {
//                 maxDisplay.innerHTML = values[handle];
//                 maxHidden.value = plainValue;
//             }
//         });
//     }

//     // --- Event Listeners ---
//     $('#select_sort').on('change', select_sort);

//     $('input:checkbox.input-check__input').on('change', function() {
//         updateFilterCounts();
//         var favs = [];
//         $('input:checkbox.input-check__input').each(function() {
//             favs.push({ id: $(this).attr('id'), value: $(this).prop('checked') });
//         });
//         localStorage.setItem("favorites", JSON.stringify(favs));
//     });
// });











































// // /**
// //  * =================================================================================
// //  * توابع عمومی (Global Functions)
// //  * این توابع باید بیرون از document.ready باشند تا از همه جا قابل دسترس باشند.
// //  * =================================================================================
// //  */

// // // تابع حذف یک پارامتر مشخص از URL
// // function removeURLParametr(url, parametr) {
// //     var urlparts = url.split('?');
// //     if (urlparts.length >= 2) {
// //         var prefix = encodeURIComponent(parametr) + '=';
// //         var pars = urlparts[1].split(/[&;]/g);
// //         for (var i = pars.length; i-- > 0;) {
// //             if (pars[i].lastIndexOf(prefix, 0) !== -1) {
// //                 pars.splice(i, 1);
// //             }
// //         }
// //         return urlparts[0] + (pars.length > 0 ? '?' + pars.join('&') : '');
// //     }
// //     return url;
// // }

// // // تابع اعمال مرتب‌سازی و ریلود صفحه
// // function select_sort() {
// //     console.log("select_sort function called!");
// //     var select_sort_value = $("#select_sort").val();
// //     var url = removeURLParametr(window.location.href, "sort_type");

// //     if (url.includes('?')) {
// //         window.location = url + "&sort_type=" + select_sort_value;
// //     } else {
// //         window.location = url + "?sort_type=" + select_sort_value;
// //     }
// // }

// // // تابع به‌روزرسانی شمارنده فیلترهای انتخاب شده (نسخه اصلاح شده)
// // function updateFilterCounts() {
// //     console.log("Updating filter counts...");

// //     // FIX: به جای widget-filters__item، هر card در آکاردئون را جداگانه بررسی می‌کنیم
// //     $('#accordion .card').each(function() {
// //         var filterSection = $(this);
// //         // عنوان داخل هر card را پیدا می‌کنیم
// //         var titleButton = filterSection.find('.filter__title');
// //         var checkedCount = filterSection.find('.input-check__input:checked').length;

// //         titleButton.find('.filter-count').remove();

// //         if (checkedCount > 0) {
// //             titleButton.append(' <span class="filter-count">' + checkedCount + '</span>');
// //         }
// //     });

// //     // این بخش برای فیلترهایی که ساختار card ندارند (مثل برند) جداگانه اجرا می‌شود
// //     $('.widget-filters__item').not(':has(#accordion)').each(function() {
// //         var filterSection = $(this);
// //         var titleButton = filterSection.find('.filter__title');
// //         var checkedCount = filterSection.find('.input-check__input:checked').length;
        
// //         titleButton.find('.filter-count').remove();

// //         if (checkedCount > 0) {
// //             titleButton.append(' <span class="filter-count">' + checkedCount + '</span>');
// //         }
// //     });
// // }
// // // تابع به‌روزرسانی شمارنده فیلترهای انتخاب شده (نسخه اصلاح شده)
// // // function updateFilterCounts() {
// // //     console.log("Updating filter counts...");

// // //     // FIX: به جای widget-filters__item، هر card در آکاردئون را جداگانه بررسی می‌کنیم
// // //     $('#accordion .card').each(function() {
// // //         var filterSection = $(this);
// // //         // عنوان داخل هر card را پیدا می‌کنیم
// // //         var titleButton = filterSection.find('.filter__title');
// // //         var checkedCount = filterSection.find('.input-check__input:checked').length;

// // //         titleButton.find('.filter-count').remove();

// // //         if (checkedCount > 0) {
// // //             titleButton.append(' <span class="filter-count">' + checkedCount + '</span>');
// // //         }
// // //     });

// //     // این بخش برای فیلترهایی که ساختار card ندارند (مثل برند) جداگانه اجرا می‌شود
// //     $('.widget-filters__item').not(':has(#accordion)').each(function() {
// //         var filterSection = $(this);
// //         var titleButton = filterSection.find('.filter__title');
// //         var checkedCount = filterSection.find('.input-check__input:checked').length;
        
// //         titleButton.find('.filter-count').remove();

// //         if (checkedCount > 0) {
// //             titleButton.append(' <span class="filter-count">' + checkedCount + '</span>');
// //         }
// //     });
// // }
// // // function updateFilterCounts() {
// // //     console.log("Updating filter counts..."); // برای تست در کنسول
// // //     $('.widget-filters__item').each(function() {
// // //         var filterSection = $(this);
// // //         var titleButton = filterSection.find('.filter__title');
// // //         var checkedCount = filterSection.find('.input-check__input:checked').length;

// // //         titleButton.find('.filter-count').remove(); // حذف شمارنده قبلی

// // //         if (checkedCount > 0) {
// // //             titleButton.append(' <span class="filter-count">' + checkedCount + '</span>');
// // //         }
// // //     });
// // // }


// // /**
// //  * =================================================================================
// //  * کدهای اجرایی پس از بارگذاری کامل صفحه (DOM Ready)
// //  * تمام کدهایی که با عناصر صفحه کار می‌کنند باید در اینجا باشند.
// //  * =================================================================================
// //  */

// // $(document).ready(function() {
// //     console.log("Document is ready. Initializing scripts.");


// //     // این کد را داخل $(document).ready(...) قرار دهید

// // // ----------- شروع کد اسلایدر قیمت -----------
// // var priceSlider = document.getElementById('price-slider');

// // if (priceSlider) {
// //     var urlParams = new URLSearchParams(window.location.search);
    
// //     // حداقل و حداکثر قیمت ممکن را از ویو دریافت می‌کنیم
// //     var absMinPrice = {{ res_aggre.min|default:0 }};
// //     var absMaxPrice = {{ res_aggre.max|default:100000000 }};

// //     // مقادیر شروع اسلایدر را از URL یا از مقادیر مطلق می‌خوانیم
// //     var startMinPrice = parseInt(urlParams.get('price_min')) || absMinPrice;
// //     var startMaxPrice = parseInt(urlParams.get('price_max')) || absMaxPrice;

// //     noUiSlider.create(priceSlider, {
// //         start: [startMinPrice, startMaxPrice], // نقاط شروع دستگیره‌ها
// //         connect: true, // رنگی کردن محدوده بین دستگیره‌ها
// //         step: 100000, // گام حرکت دستگیره‌ها
// //         range: {
// //             'min': absMinPrice,
// //             'max': absMaxPrice
// //         },
// //         // برای نمایش اعداد به صورت خوانا (مثلا ۱,۰۰۰,۰۰۰)
// //         format: {
// //           to: function (value) {
// //             return Math.round(value).toLocaleString();
// //           },
// //           from: function (value) {
// //             return Number(value.replace(/,/g, ''));
// //           }
// //         }
// //     });

// //     var minDisplay = document.getElementById('price-min-display');
// //     var maxDisplay = document.getElementById('price-max-display');
// //     var minHiddenInput = document.getElementById('price_min_hidden');
// //     var maxHiddenInput = document.getElementById('price_max_hidden');

// //     // رویدادی که با هر حرکت دستگیره‌ها اجرا می‌شود
// //     priceSlider.noUiSlider.on('update', function (values, handle) {
// //         var plainValue = Number(values[handle].replace(/,/g, '')); // مقدار عددی و بدون کاما
// //         if (handle === 0) { // دستگیره چپ (حداقل)
// //             minDisplay.innerHTML = values[handle];
// //             minHiddenInput.value = plainValue;
// //         } else { // دستگیره راست (حداکثر)
// //             maxDisplay.innerHTML = values[handle];
// //             maxHiddenInput.value = plainValue;
// //         }
// //     });
// // }
// // // ----------- پایان کد اسلایدر قیمت -----------

// //     // ------------------ راه‌اندازی اولیه در زمان بارگذاری صفحه ------------------

// //     // ۱. به‌روزرسانی اولیه شمارنده فیلترها
// //     updateFilterCounts();

// //     // ۲. مدیریت دکمه "حذف فیلترها"
// //     var urlParams = new URLSearchParams(window.location.search);
// //     urlParams.delete('page'); // پارامتر صفحه‌بندی را نادیده بگیر
// //     if (urlParams.toString() !== "") {
// //         $('#reset_filters_btn').css('display', 'inline-block');
// //     }

// //     // ۳. بازیابی وضعیت چک‌باکس‌ها از حافظه مرورگر (localStorage)
// //     var favorites = JSON.parse(localStorage.getItem('favorites'));
// //     if (favorites) {
// //         favorites.forEach(function(fav) {
// //             var element = $('#' + fav.id);
// //             if (element.length) {
// //                 element.prop('checked', fav.value);
// //             }
// //         });
// //         // پس از بازیابی وضعیت، دوباره شمارنده‌ها را به‌روز کن
// //         updateFilterCounts(); 
// //     }

// //     // ------------------ تعریف Event Listener ها ------------------

// //     // ۱. رویداد برای دکمه مرتب‌سازی
// //     $('#select_sort').on('change', select_sort);

// //     // ۲. رویداد برای ذخیره وضعیت چک‌باکس‌ها در حافظه و به‌روزرسانی شمارنده
// //     $('input:checkbox.input-check__input').on('change', function() {
// //         // ابتدا شمارنده را به‌روز کن
// //         updateFilterCounts();

// //         // سپس وضعیت را در حافظه ذخیره کن
// //         var favs = [];
// //         $('input:checkbox.input-check__input').each(function() {
// //             favs.push({ id: $(this).attr('id'), value: $(this).prop('checked') });
// //         });
// //         localStorage.setItem("favorites", JSON.stringify(favs));
// //     });
// // });












// // // // این تابع باید در سطح عمومی باشد تا در دسترس باشد
// // // function removeURLParametr(url, parametr) {
// // //     var urlparts = url.split('?');
// // //     if (urlparts.length >= 2) {
// // //         var prefix = encodeURIComponent(parametr) + '=';
// // //         var pars = urlparts[1].split(/[&;]/g);
// // //         for (var i = pars.length; i-- > 0;) {
// // //             if (pars[i].lastIndexOf(prefix, 0) !== -1) {
// // //                 pars.splice(i, 1);
// // //             }
// // //         }
// // //         return urlparts[0] + (pars.length > 0 ? '?' + pars.join('&') : '');
// // //     }
// // //     return url;
// // // }

// // // // این تابع هم باید در سطح عمومی باشد
// // // function select_sort() {
// // //     // این پیغام برای تست در کنسول نمایش داده می‌شود
// // //     console.log("select_sort function called!"); 

// // //     var select_sort_value = $("#select_sort").val();
// // //     var url = removeURLParametr(window.location.href, "sort_type");

// // //     if (url.includes('?')) {
// // //         window.location = url + "&sort_type=" + select_sort_value;
// // //     } else {
// // //         window.location = url + "?sort_type=" + select_sort_value;
// // //     }
// // // }



// // // // این تابع را بیرون از document.ready تعریف کنید
// // // function updateFilterCounts() {
// // //     // برای هر بخش از فیلتر (مثل برند، ویژگی‌ها و ...)
// // //     $('.filter').each(function() {
// // //         var filterSection = $(this);
// // //         var titleButton = filterSection.find('.filter__title');
// // //         var checkedCount = filterSection.find('.input-check__input:checked').length;

// // //         // ابتدا شمارنده قبلی را حذف می‌کنیم
// // //         titleButton.find('.filter-count').remove();

// // //         // اگر آیتمی انتخاب شده بود، شمارنده جدید را اضافه می‌کنیم
// // //         if (checkedCount > 0) {
// // //             titleButton.append(' <span class="filter-count">' + checkedCount + '</span>');
// // //         }
// // //     });
// // // }


// // // $(document).ready(function() {
// // //     console.log("Document is ready.");

// // // // ////////////////////////////////////////////////////////////    // 

// // // // این دو خط را در داخل $(document).ready(function() { ... }); قرار دهید

// // // // در زمان بارگذاری صفحه، شمارنده‌ها را به‌روز کن
// // // updateFilterCounts();

// // // // با هر بار کلیک روی یک چک‌باکس، دوباره شمارنده‌ها را به‌روز کن
// // // $('.input-check__input').on('change', updateFilterCounts);

// // // // /////////////////////////////////////////////////////////////////

// // //     // این کد را در داخل $(document).ready(function() { ... }); قرار دهید

// // //     var urlParams = new URLSearchParams(window.location.search);

// // //     // پارامتر 'page' را حذف می‌کنیم تا در محاسبات ما به عنوان فیلتر شناخته نشود
// // //     urlParams.delete('page');

// // //     // اگر بعد از حذف 'page'، هنوز پارامتری وجود داشت، یعنی فیلتری فعال است
// // //     if (urlParams.toString() !== "") {
// // //         $('#reset_filters_btn').css('display', 'inline-block');
// // //         }
// // // // /////////////////////////////////////////////////////////////////
// // //     // ۱. اتصال رویداد به مرتب‌سازی (بخش سالم)
// // //     $('#select_sort').on('change', select_sort);

// // //     // ۲. مدیریت دکمه "دارای فیلتر" (بخش سالم)
// // //     var urlParams = new URLSearchParams(window.location.search);
// // //     if (urlParams.toString() === "") {
// // //         localStorage.clear();
// // //         $("#filter_state").css("display", "none");
// // //     } else {
// // //         $("#filter_state").css("display", "inline-block");
// // //     }

// // //     // ۳. مدیریت ذخیره چک‌باکس‌ها (بخش سالم)
// // //     $('input:checkbox').on('click', function() {
// // //         var favs = [];
// // //         $('input:checkbox').each(function() {
// // //             favs.push({ id: $(this).attr('id'), value: $(this).prop('checked') });
// // //         });
// // //         localStorage.setItem("favorites", JSON.stringify(favs));
// // //     });

// // //     // ۴. بازیابی وضعیت چک‌باکس‌ها (نسخه امن و اصلاح شده)
// // //     var favorites = JSON.parse(localStorage.getItem('favorites'));
// // //     if (favorites) {
// // //         favorites.forEach(function(fav) {
// // //             var element = $('#' + fav.id);
// // //             // فقط در صورتی مقدار را تغییر بده که عنصر در صفحه وجود داشته باشد
// // //             if (element.length) {
// // //                 element.prop('checked', fav.value);
// // //             }
// // //         });
// // //     }
// // // });

// // // // این تابع باید در سطح عمومی باشد تا در دسترس باشد
// // // function removeURLParametr(url, parametr) {
// // //     var urlparts = url.split('?');
// // //     if (urlparts.length >= 2) {
// // //         var prefix = encodeURIComponent(parametr) + '=';
// // //         var pars = urlparts[1].split(/[&;]/g);
// // //         for (var i = pars.length; i-- > 0;) {
// // //             if (pars[i].lastIndexOf(prefix, 0) !== -1) {
// // //                 pars.splice(i, 1);
// // //             }
// // //         }
// // //         return urlparts[0] + (pars.length > 0 ? '?' + pars.join('&') : '');
// // //     }
// // //     return url;
// // // }

// // // // این تابع هم باید در سطح عمومی باشد
// // // function select_sort() {
// // //     // این پیغام برای تست در کنسول نمایش داده می‌شود
// // //     console.log("select_sort function called!"); 

// // //     var select_sort_value = $("#select_sort").val();
// // //     var url = removeURLParametr(window.location.href, "sort_type");

// // //     if (url.includes('?')) {
// // //         window.location = url + "&sort_type=" + select_sort_value;
// // //     } else {
// // //         window.location = url + "?sort_type=" + select_sort_value;
// // //     }
// // // }


// // // // کدی که با بارگذاری کامل صفحه اجرا می‌شود
// // // $(document).ready(function() {

// // //     // این پیغام برای تست در کنسول نمایش داده می‌شود
// // //     console.log("Document is ready. Attaching event listener.");

// // //     // اتصال رویداد 'change' به عنصر با آیدی select_sort
// // //     // این جایگزین onchange در HTML است
// // //     $('#select_sort').on('change', function() {
// // //         select_sort();
// // //     });
    
// // //     // بقیه کدهای مربوط به localStorage و فیلترها می‌تواند اینجا باشد
// // //     var urlParams = new URLSearchParams(window.location.search);
// // //     if (urlParams.toString() === "") {
// // //         localStorage.clear();
// // //         $("#filter_state").css("display", "none");
// // //     } else {
// // //         $("#filter_state").css("display", "inline-block");
// // //     }

// // //     // ... بقیه کدهای شما
// // // });







// // // $(document).ready(function() {
// // //     // FIX 1: The correct way to check for empty URL parameters
// // //     var urlParams = new URLSearchParams(window.location.search);
// // //     if (urlParams.toString() === "") {
// // //         localStorage.clear();
// // //         $("#filter_state").css("display", "none");
// // //     } else {
// // //         $("#filter_state").css("display", "inline-block");
// // //     }

// // //     // This logic is fine
// // //     $('input:checkbox').on('click', function() {
// // //         var fav, favs = [];
// // //         $('input:checkbox').each(function() {
// // //             fav = { id: $(this).attr('id'), value: $(this).prop('checked') };
// // //             favs.push(fav);
// // //         });
// // //         localStorage.setItem("favorites", JSON.stringify(favs));
// // //     });

// // //     // FIX 2: Check if 'favorites' exists in localStorage to prevent errors
// // //     var favorites = JSON.parse(localStorage.getItem('favorites'));
// // //     if (favorites) {
// // //         for (var i = 0; i < favorites.length; i++) {
// // //             // Ensure the element exists before trying to modify it
// // //             if ($('#' + favorites[i].id).length) {
// // //                 $('#' + favorites[i].id).prop('checked', favorites[i].value);
// // //             }
// // //         }
// // //     }
// // // });

// // // function showVal(x) {
// // //     // This logic is fine
// // //     x = x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
// // //     // It's better to check if the element exists
// // //     if ($('#sel_price').length) {
// // //         $('#sel_price').text(x);
// // //     }
// // // }

// // // // This function is fine
// // // function removeURLParametr(url, parametr) {
// // //     var urlparts = url.split('?');
// // //     if (urlparts.length >= 2) {
// // //         var prefix = encodeURIComponent(parametr) + '=';
// // //         var pars = urlparts[1].split(/[&;]/g);
// // //         for (var i = pars.length; i-- > 0;) {
// // //             if (pars[i].lastIndexOf(prefix, 0) !== -1) {
// // //                 pars.splice(i, 1);
// // //             }
// // //         }
// // //         return urlparts[0] + (pars.length > 0 ? '?' + pars.join('&') : '');
// // //     }
// // //     return url;
// // // }

// // // // تابع انتخاب مدل مرتب سازی
// // // function select_sort() {
// // //     var select_sort_value = $("#select_sort").val();
// // //     var url = removeURLParametr(window.location.href, "sort_type");

// // //     // FIX 3: Correctly append the sort parameter using '?' or '&'
// // //     if (url.includes('?')) {
// // //         window.location = url + "&sort_type=" + select_sort_value;
// // //     } else {
// // //         window.location = url + "?sort_type=" + select_sort_value;
// // //     }
// // // }

// // // function add_to_shop_cart(product_id, tedad) {
// // //     // FIX 4: The first alert was likely for debugging and was syntactically incorrect. Removed it.
// // //     $.ajax({
// // //         type: "GET",
// // //         url: "/orders/add_to_shop_cart/",
// // //         data: {
// // //             product_id: product_id,
// // //             tedad: tedad,
// // //         },
// // //         success: function(res) {
// // //             alert("کالای مورد نظر به سبد خرید شما اضافه شد");
// // //             $("#indicator__value").text(res);
// // //         }
// // //     });
// // // }

// // // function delete_from_shop_cart(product_id) {
// // //     $.ajax({
// // //         type: "GET",
// // //         url: "/orders/delete_from_shop_cart/",
// // //         data: {
// // //             product_id: product_id,
// // //         },
// // //         success: function(res) {
// // //             alert("کالای مورد نظر از سبد خرید شما حذف شد");
// // //             $("#shop_cart_list").html(res);
// // //         }
// // //     });
// // // }













// // // $(document).ready(
// // //     function(){
// // //         var urlParams=new URLSearchParams(window.location.search);
// // //         if(urlParams==""){
// // //             localStorage.clear();
// // //             $("#filter_state").css("display","none");
// // //         }else{
// // //             $("#filter_state").css("display","inline-block");
// // //         }
// // //         $('input:checkbox').on('click',function(){
// // //             var fav,favs=[];
// // //             $('input:checkbox').each(function(){
// // //                 fav={id:$(this).attr('id'),value:$(this).prop('checked')};
// // //                 favs.push(fav);
// // //             })
// // //             localStorage.setItem("favorites",JSON.stringify(favs));
// // //         })
// // //         var favorites=JSON.parse(localStorage.getItem('favorites'));
       
// // //         for(var i = 0; i < favorites.length; i++){
// // //             $('#' + favorites[i].id).prop('checked', favorites[i].value);
// // //         }
// // //     }
// // // );




// // // function showVal(x) {
// // //     x=x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
// // //     document.getElementById('sel_price').innerText=x;
// // // }



// // // // تابع حذف پارامتر های خط آدرس
// // // function removeURLParametr(url,parametr){
// // //     var urlparts = url.split('?');
// // //     if (urlparts.length >= 2){
// // //         var prefix = encodeURIComponent(parametr) + '=';
// // //         var pars = urlparts[1].split(/[&;]/g);
// // //         for (var i = pars.length; i-- > 0;) {
// // //             if (pars[i].lastIndexOf(prefix,0) !== -1){
// // //                 pars.splice(i,1);
// // //             }
// // //         }
// // //         return urlparts[0] + (pars.length > 0 ? '?' + pars.join('&') : '');
// // //     }
// // //     return url;
// // // }




// // // // تابع انتخاب مدل مرتب سازی
// // // function select_sort(){
// // //     var select_sort_value = $("#select_sort").val();
// // //     var url=removeURLParametr(window.location.href,"sort_type");
// // //     window.location  = url + "&sort_type=" + select_sort_value;
// // // }



// // // function add_to_shop_cart(product_id,tedad){
// // //     alert(product_id+"",tedad);
// // //     $.ajax({
// // //         type:"GET",
// // //         url:"/orders/add_to_shop_cart/",
// // //         data:{
// // //             product_id: product_id,
// // //             tedad: tedad,
// // //         },
// // //         success:function(res){
// // //             alert("کالای مورد نظر به سبد خرید شما اضافه شد");
// // //             $("#indicator__value").text(res);
// // //         }
// // //     });

// // // }


// // // function delete_from_shop_cart(product_id){
// // //     $.ajax({
// // //         type:"GET",
// // //         url:"/orders/delete_from_shop_cart/",
// // //         data:{
// // //             product_id:product_id,
// // //         },
// // //         success:function(res){
// // //             alert("کالای مورد نظر از سبد خرید شما حذف شد");
// // //             $("#shop_cart_list").html(res);
// // //         }
// // //     });
// // // }