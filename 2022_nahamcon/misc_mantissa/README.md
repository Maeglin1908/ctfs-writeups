# Mantissa

This challenge requires to get the solution of the following math :

`(x) == (x+1)`

That make me think to integer overflow.


We know that the program perform this code : 

```js
console.log(...)
```

So we can guess this is JavaScript.

[Javascript Max Integer](https://www.programiz.com/javascript/library/number/max_safe_integer)

From that, we can run a quick JS Script : 

```js
let pas = Number.MAX_SAFE_INTEGER-10
for (let i = pas; i<pas*2; i++){
  
  console.log(i)
  if (i == (i + 1)){
    console.log(i)
    break
  }
}
```

```node
> node test.js
9007199254740981
9007199254740982
9007199254740983
9007199254740984
9007199254740985
9007199254740986
9007199254740987
9007199254740988
9007199254740989
9007199254740990
9007199254740991
9007199254740992
9007199254740992
```

9007199254740992 Is the solution !