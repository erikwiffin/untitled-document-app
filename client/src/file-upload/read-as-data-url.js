export const readAsDataURL = async (file) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.addEventListener('load', () => {
      resolve(reader.result);
    });

    reader.readAsDataURL(file);
  });
};
