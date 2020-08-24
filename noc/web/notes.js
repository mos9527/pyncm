/*
 * @Author: greats3an
 * @Date: 2020-01-20 21:06:51
 * @LastEditors  : greats3an
 * @LastEditTime : 2020-02-05 20:39:14
 * @Site: mos9527.tooo.top
 * @Description: core.js 逆向分析
 */

/*
    Analyzing encText & encKey
    (I'll refer them as the NCMEncrypt)
*/
/*
The window.asrsea function is the last function called before genearting the NCMEncrypt values.
After analyzing the break point,here's the core part:
*/

UJ6D.md = ["色", "流感", "这边", "弱", "嘴唇", "亲", "开心", "呲牙", "憨笑", "猫", "皱眉", "幽灵", "蛋糕", "发怒", "大哭", "兔子", "星星", "钟情", "牵手", "公鸡", "爱意", "禁止", "狗", "亲亲", "叉", "礼物", "晕", "呆", "生病", "钻石", "拜", "怒", "示爱", "汗", "小鸡", "痛苦", "撇嘴", "惶恐", "口罩", "吐舌", "心碎", "生气", "可爱", "鬼脸", "跳舞", "男孩", "奸笑", "猪", "圈", "便便", "外星", "圣诞"]
window.asrsea(JSON.stringify(i0x), bjG0x(["流泪", "强"]), bjG0x(UJ6D.md), bjG0x(["爱心", "女孩", "惊恐", "大笑"]));

// Let's see how bjG0x works...
var bjG0x = function (cId8V) {
    // cId8V is a list object
    var m0x = [];
    k0x.be1x(cId8V, function (cIb8T) {
        m0x.push(UJ6D.emj[cIb8T])
    });
    // two arguments are passed.Let's see k0x.be1x
    return m0x.join("")
};
k0x.be1x = function (j0x, cD1x, O0x) {
    if (!j0x || !j0x.length || !k0x.gQ4U(cD1x))
        // if j0x is empty,doesn't match.go on.
        return this;
    if (!!j0x.forEach) {
        // if j0x is iterable,match
        j0x.forEach(cD1x, O0x);//O0x is empty and not used here
        //for every item in j0x,do cD1x(item)
        return this
    }
	/* ignore these because the code won't go this far
	for (var i = 0, l = j0x.length; i < l; i++)
		//go through 
		cD1x.call(O0x, j0x[i], i, j0x);
	return this */
}
// the simplied bjG0x looks like this:
var bjG0x = function (input) {
    var arr = [];
    function push_into_array(i) {
        arr.push(UJ6D.emj[i]);
    }
    input.forEach(push_into_array)
    return arr.join("")
};
// now we can see it actually translates every word of the input into the UJ6D.emj version
// then pushes it into the array,then returns the joined array
// What's UJ6D.emj,then?
UJ6D.emj = {
    "色": "00e0b",
    "流感": "509f6",
    "这边": "259df",
    "弱": "8642d",
    "嘴唇": "bc356",
    "亲": "62901",
    "开心": "477df",
    "呲牙": "22677",
    "憨笑": "ec152",
    "猫": "b5ff6",
    "皱眉": "8ace6",
    "幽灵": "15bb7",
    "蛋糕": "b7251",
    "发怒": "52b3a",
    "大哭": "b17a8",
    "兔子": "76aea",
    "星星": "8a5aa",
    "钟情": "76d2e",
    "牵手": "41762",
    "公鸡": "9ec4e",
    "爱意": "e341f",
    "禁止": "56135",
    "狗": "fccf6",
    "亲亲": "95280",
    "叉": "104e0",
    "礼物": "312ec",
    "晕": "bda92",
    "呆": "557c9",
    "生病": "38701",
    "钻石": "14af6",
    "拜": "c9d05",
    "怒": "c4f7f",
    "示爱": "0c368",
    "汗": "5b7a4",
    "小鸡": "6bee2",
    "痛苦": "55932",
    "撇嘴": "575cc",
    "惶恐": "e10b4",
    "口罩": "24d81",
    "吐舌": "3cfe4",
    "心碎": "875d3",
    "生气": "e8204",
    "可爱": "7b97d",
    "鬼脸": "def52",
    "跳舞": "741d5",
    "男孩": "46b8e",
    "奸笑": "289dc",
    "猪": "6935b",
    "圈": "3ece0",
    "便便": "462db",
    "外星": "0a22b",
    "圣诞": "8e7",
    "流泪": "01000",
    "强": "1",
    "爱心": "0CoJU",
    "女孩": "m6Qyw",
    "惊恐": "8W8ju",
    "大笑": "d"
};
// and yes,it is a dictionary.
/* As the dictionary is fixed,and the arguments passed are also constant,
   These following funtions also reutrns a constant result
bjG0x(["流泪", "强"]):
    "010001"
bjG0x(UJ6D.md):
    "00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7"
bjG0x(["爱心", "女孩", "惊恐", "大笑"]):
    "0CoJUm6Qyw8W8jud"
*/
//It's just easier if we treat them as a constant
//To simplify a bit,here's how the function looks like now:
window.asrsea(
    JSON.stringify(i0x),
    "010001",
    "00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7",
    "0CoJUm6Qyw8W8jud"
);
//But what exactly IS window.asrsea?
//After a quick-n-dirty search.it seems like...
function d(d, e, f, g) {
    var h = {}, i = a(16);
    return h.encText = b(d, g),
        h.encText = b(h.encText, i),
        h.encSecKey = c(i, e, f),
        h
}
window.asrsea = d
//Ah-ha!window.asrsea is d
//Now the code looks like THIS:
function d(d, e, f, g) {
    //for d,it's the plain text
    //for e,it's 010001,the modulus
    //for f,it's [the very-very long argument],the rsa pubkey
    //for g,it's 0CoJUm6Qyw8W8jud,the aes key
    var h = {}, i = a(16);
    return h.encText = b(d, g),
        h.encText = b(h.encText, i),
        h.encSecKey = c(i, e, f),
        h
}
d(
    JSON.stringify(i0x),
    "010001",
    "00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7",
    "0CoJUm6Qyw8W8jud"
);
//where in [d],more functions(a,b,c) are called.Let's find them!
function a(a) {
    var d, e, b = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", c = "";
    for (d = 0; a > d; d += 1)
        e = Math.random() * b.length,
            e = Math.floor(e),
            c += b.charAt(e);
    return c
}
//a...which generates a random string lengths [a] characters,it will be used as a seed
function b(a, b) {
    // var a is the plain text
    // var b is supposingly,an AES key
    var c = CryptoJS.enc.Utf8.parse(b)
        // KEY
        , d = CryptoJS.enc.Utf8.parse("0102030405060708")
        // IV
        , e = CryptoJS.enc.Utf8.parse(a)
        // plain text
        // the syntax of CryptoJS.AES.encrypt is:
        //    CryptoJS.AES.encrypt(str, key, options);
        , f = CryptoJS.AES.encrypt(e, c, {
            iv: d,
            mode: CryptoJS.mode.CBC
        });
    return f.toString()
}
//b...which is an AES implementation.see the comments above
//which generates an encrypted string[a] with key[b] and iv[0102030405060708]
function c(a, b, c) {
    var d, e;
    return setMaxDigits(131),
        d = new RSAKeyPair(b, "", c),
        e = encryptedString(d, a)
}
//c...which is a RSA implementaion.which generates an encrypted string[a] with modulus[b] and publickey[c] 

//That's the break down.Let's go back tp the point!

/* PWNing NCMEncrypt */

/*====Generating h.encText:
h.encText in the first argument is an AES Encrypted version of the plain text
Since I know shit about cryptography,i'll just describe them as
AES CBC key:IV and RSA modulus:publickey

plain text ----AES CBC key:0CoJUm6Qyw8W8jud,IV:0102030405060708----> h.encText

Then,the encrypted h.encText got encrypted AGAIN,this time,with the SEED as the key.

h.encText ----AES CBC key:(SEED),IV:0102030405060708 ----> h.encText

Finally,we got the encText agrumnent
Where in the XHR,the h.encText is [params] in the POST Body
*/

/*====Generating h.encSecKey
The encSecKey is bound to the SEED,nothing else would change it
    (SEED) ----RSA modulus[010001],publickey[the very-very-long string]----> encSecKey

However,RSA is meant to be decrypted with a public key
In this case,the public key is a constant string
Also,the SEED does not need to be unique every time the request is made

It's up to you to decide whether or not should you implement this feature,mine did
*/

/*
Congratulations! You now have generated both cryptic arguments
Now the plain text part isn't simply the id of the music nor a constant string.It's a json containing
The method and the arguments used to specify the content

The plain text is stored in the i0x variable
I've caught some along with the api address and wrote it in the Python port

When requesting,as you already know,you should
POST to the url to the API correspondingly.But there's another trick you should remember:
    When requesting,make the User-Agent different every time
    To avoid scrapper checking

Also,you need these headers specified to work:
    User-Agent:(anything reasonable)
    Host:music.163.com
    Content-Type:x-www-form-urlencoded
*/


/*
Analyzing csrf_token
*/

i0x["csrf_token"] = v0x.gS4W("__csrf");
// csrf_token is generated by v0x.gS4W
var c0x = NEJ.P,
    v0x = c0x("nej.j")
// where v0x is declared this way,refercing c0x,which is NEJ.P
// to simplfiy that,the csrf_token is generated through this function:
NEJ.P("nej.j").gS4W('__csrf');
// let's analyze NEJ.P
NEJ.P = function (Kj2x) {
    if (!Kj2x || !Kj2x.length)
        return null;
    // checks whether Kj2x has content or not 
    var Zy7r = window;
    // assaigns Zy7r to window...why?
    /*
    for (var a = Kj2x.split("."), l = a.length, i = a[0] == "window" ? 1 : 0; i < l; Zy7r = Zy7r[a[i]] = Zy7r[a[i]] || {},i++);
    this is the original code,i simplied a bit to be more readable
    */
    var a = Kj2x.split(".")
    // splits the argument by [.]
    /* we have nej.j here,which is 
    0: "nej"
    1: "j"
    length: 2
    */
    l = a.length
    i = a[0] == "window" ? 1 : 0
    // i is whether split[0] is 'window' (1) or not(0).here,it's 0
    while (i < l) {
        Zy7r = Zy7r[a[i]] = Zy7r[a[i]] || {}
        i++
    }
    // a loop where will finally makes Zy7r into window[a[0]][a[1]]
    return Zy7r
}
// there goes NEJ.P,inputs a string ('A.B'),returns window[A][B]
// the function now looks like this
window['nej']['j'].gS4W('__csrf');
// let's find out what gS4W is!
j.gS4W = function () {
    var dg2x = new Date
        , cqP4T = +dg2x
        , bvl3x = 864e5;
    var crc4g = function (Y1x) {
        var sy8q = document.cookie
            , tY8Q = "\\b" + Y1x + "="
            , bft9k = sy8q.search(tY8Q);
        if (bft9k < 0)
            return "";
        bft9k += tY8Q.length - 2;
        var zd9U = sy8q.indexOf(";", bft9k);
        if (zd9U < 0)
            zd9U = sy8q.length;
        return sy8q.substring(bft9k, zd9U) || ""
    };
    return function (Y1x, i0x) {
        if (i0x === undefined)
            return crc4g(Y1x);
        if (u.fO4S(i0x)) {
            if (!!i0x) {
                document.cookie = Y1x + "=" + i0x + ";";
                return i0x
            }
            i0x = {
                expires: -100
            }
        }
        i0x = i0x || o;
        var sy8q = Y1x + "=" + (i0x.value || "") + ";";
        delete i0x.value;
        if (i0x.expires !== undefined) {
            dg2x.setTime(cqP4T + i0x.expires * bvl3x);
            i0x.expires = dg2x.toGMTString()
        }
        sy8q += u.vJ8B(i0x, ";");
        document.cookie = sy8q
    }
}
//Looks like we are calling crc4g('__csrf')
//Which gets __csrf value from the cookies...disapointed..

//Let's find WHEN did __csrf got added into the cookie jar
//....which is in the LOGIN section...let's focus on that.
//Adding breakpoints at the window.asrsea function
// i0x is another JSON object,which looks like this:
i0x = { "phone": "16942066669", "password": "DEADBEEFBAADF00D", "rememberLogin": "true", "checkToken": "deadc0de696969694206669527", "csrf_token": "" }
// the phone number is in plain text.
// and the 16 characters 'password',well,it must be a HASH.
// turns out,the password IS a MD5-Hash.
// so,i0x is half done.

// After some digging,It turns out that checkToken isn't necessary.
// You can leave it empty and the server will STILL return the result.
// Let's forget about that.
// The i0x now looks like THIS:
i0x = {
    "phone": "(your phone number)",
    "password": "(your password's md5 value)",
    "rememberLogin": "true",
    "checkToken": "",
    "csrf_token": ""
}
// Now,you may generate those login info with the format given.
// Then send the NCMEncrypt-version of the stringified JSON to the login server:https://music.163.com/weapi/login/cellphone
// I'm using cellphone login.You may dig your self to find a username version
// Then the new cookies comes in.But remeber that you should apply the CSRF token into the i0x plain text's CSRF area.
// Now you're done!Fell free to download some VIP music and PWN everyday!