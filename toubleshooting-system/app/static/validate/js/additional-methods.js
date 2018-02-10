/**
 * Created by Administrator on 2017/8/9.
 */
jQuery.validator.addMethod("ipv4", function(value, element) {
    var ipv4 = /^(25[0-5]|2[0-4]\d|[0-1]?\d?\d)(\.(25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3}$/;
    return this.optional(element) || (ipv4.test(value));
}, "请正确填写IP地址");


jQuery.validator.addMethod("yewuip", function(value, element) {
    var yewuip = /^((25[0-5]|2[0-4]\d|[0-1]?\d?\d)(\.(25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3}|(25[0-5]|2[0-4]\d|[0-1]?\d?\d)(\.(25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3}\/(\d|[1-2]\d|3[0-2])|(25[0-5]|2[0-4]\d|[0-1]?\d?\d)(\.(25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3}-(25[0-5]|2[0-4]\d|[0-1]?\d?\d))$/;
    return this.optional(element) || (yewuip.test(value));
}, "请正确填写业务IP地址");