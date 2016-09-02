// (function () {
//     'use strict';

//     var _t = openerp._t;
//     var website = openerp.website;
//     website.ready().done(function() {
//     openerp.Tour.register({
//          id:   'tourdemo_seo',                 
//         name: _t("Demo SEO Tour"),            
      
//         steps:  steps: [
//               {
//               title:     _t("Welcome to your website!"),
//                 content:   _t("This tutorial will guide you to build seo suit for your home page. We will start by -----------."),
//                 popover:   { next: _t("Start Tutorial"), end: _t("Skip It") },
//               },
//             {
//                 element:   'button[data-action=edit]', 
//                 placement: 'bottom',                   
//                 title:     _t("Edit this page"),
//                 content:   _t("Every Product of your website  can be made popular by   through SEOthe <i>Edit</i> button."),
//                 popover:   { fixed: true },            
//             },
//             ]
//     });
//     });

// }());

// (function () {
//     'use strict';

//     var _t = openerp._t;
//     var website = openerp.website;
//     website.ready().done(function() {
//     openerp.Tour.register({
//         id:   'blog_seo',
//         name: _t("Create a blog post"),
//         steps: [
//             {
//                 title:     _t("New Blog Post"),
//                 content:   _t("Let's go through the first steps to write beautiful blog posts."),
//                 popover:   { next: _t("Start Tutorial"), end: _t("Skip") },
//             },
//             {
//                 element:   '#content-menu-button',
//                 placement: 'left',
//                 title:     _t("Add Content"),
//                 content:   _t("Use this <em>'Content'</em> menu to create a new blog post like any other document (page, menu, products, event, ...)."),
//                 popover:   { fixed: true },
//             },
//         ]
//         });
//     });
// });

(function () {
    website.Tour.register({               
        id:   'tourdemoseo',                 
        name: _t("Demo Tour"),            
        path: '/page/homepage',           
        steps: [                          
            {
                title:     _t("Welcome to your website!"),
                content:   _t("This tutorial will guide you to build your home page. We will start by adding a banner."),
                popover:   { next: _t("Start Tutorial"), end: _t("Skip It") },
            },
            {
                element:   'button[data-action=edit]', 
                placement: 'bottom',                   
                title:     _t("Edit this page"),
                content:   _t("Every page of your website can be modified through the <i>Edit</i> button."),
                popover:   { fixed: true },            
            },
            {
                snippet:   '#snippet_structure .oe_snippet:first',
                placement: 'bottom',
                title:     _t("Drag & Drop a Banner"),
                content:   _t("Drag the Banner block and drop it in your page."),
                popover:   { fixed: true },
            },
            {
                element:   'button[data-action=save]',
                placement: 'right',
                title:     _t("Save your modifications"),
                content:   _t("Publish your page by clicking on the <em>'Save'</em> button."),
                popover:   { fixed: true },
            },
            {
                waitFor:   'button[data-action=save]:not(:visible)',
                title:     _t("Good Job!"),
                content:   _t("Well done, you created your homepage."),
                popover:   { next: _t("Continue") },
            },
            ]
    });
});