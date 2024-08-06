document.addEventListener("DOMContentLoaded", function () {
  const progressBar = document.getElementById("progress-bar");
  const images = document.querySelectorAll(".loading-image");

  async function startImageGeneration() {
    await fetch("/start_image_generation", { method: "POST" });
  }

  async function fetchBackendProgress() {
    try {
      const response = await fetch("/progress"); // 백엔드에서 진행률을 가져오는 엔드포인트
      if (!response.ok) throw new Error("Network response was not ok");
      const data = await response.json();
      return data.progress; // 예: { progress: 75 }
    } catch (error) {
      console.error("There was a problem with the fetch operation:", error);
      return 0;
    }
  }

  async function updateProgressBar() {
    const progress = await fetchBackendProgress();
    progressBar.style.width = progress + "%";

    if (progress >= 100) {
      clearInterval(progressInterval);
      showImages(images);
    }
  }

  function showImages(images) {
    let currentIndex = 0;

    function showNextImage() {
      if (currentIndex > 0) {
        images[currentIndex - 1].style.opacity = 0;
        images[currentIndex - 1].style.transform = "scale(0.8)";
      }

      if (currentIndex < images.length) {
        images[currentIndex].style.opacity = 1;
        images[currentIndex].style.transform = "scale(1)";
        setTimeout(() => {
          images[currentIndex].style.opacity = 0;
          images[currentIndex].style.transform = "scale(0.8)";
          currentIndex++;
          setTimeout(showNextImage, 3000); // 이미지가 떠있는 시간을 더 길게 조정
        }, 3000); // 이미지가 떠있는 시간을 더 길게 조정
      }
    }

    showNextImage();
  }

  startImageGeneration();
  const progressInterval = setInterval(updateProgressBar, 300);
});
