module.exports = class Utils {
  randomNum(Min, Max) {
    let Range = Max - Min;
    let Rand = Math.random();
    return Min + Math.round(Rand * Range); //四舍五入
  }

  timeout(delay) {
    return new Promise((resolve, reject) => {
      setTimeout(() => {
        try {
          resolve(1)
        } catch (e) {
          reject(0)
        }
      }, delay);
    })
  }
};
