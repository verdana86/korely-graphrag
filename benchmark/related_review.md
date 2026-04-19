# Related-questions ground truth — human review

**Generated:** Gemini proposals over 20 seed posts. You review the checkboxes.

**How to use:**
1. For each seed, read the abstract and the proposed links.
2. Keep `[x]` only the truly related posts. Untick `[ ]` anything weak.
3. In the 'Rejected' section, tick `[x]` any post Gemini wrongly rejected that you think IS related.
4. Save the file. Then run `build_related_questions.py` to patch the benchmark.

**Discipline:** precision over recall. Marginal links hurt the ground truth.

---
## Seed 1/20: 2026-02-12-microgpt
_id: `e6b06557-6d65-4ee6-9790-07e60f065019` · mentions in graph: 10_

> <style> .post-header h1 {     font-size: 35px; } .post pre, .post code {     background-color: #fcfcfc;     font-size: 13px; /* make code smaller for this post... */ } </style>  This is a brief guide to my new art project [microgpt](https://gist.github.com/karpathy/8627fe009c40f57531cb18360106ce95),...

**Gemini proposes these as RELATED** — tick [x] to KEEP, clear [ ] to DROP:

- [x] `2e701e80-befb-4258-a53a-fb204df46181` — **2021-03-27-forward-pass**
  - _reason: Both posts explicitly discuss GPT models, with the seed post introducing 'microgpt' and the candidate post referencing 'GPT-3' in the context of a Turing Test._
- [x] `649acfbf-16a7-47ef-8a33-51f49f01b7e1` — **nntutorial**
  - _reason: The seed post describes 'microgpt' as a guide to training and inferencing a GPT, which is a type of neural network, and the candidate post is titled 'Hacker's guide to Neural Networks' and discusses deep learning._
- [x] `58f62ce2-923d-436d-bca2-c6a5c3e18ef3` — **2015-05-21-rnn-effectiveness**
  - _reason: The seed post discusses 'microgpt', a type of GPT, which falls under the broader category of neural networks, and the candidate post discusses Recurrent Neural Networks (RNNs) and their effectiveness._
- [x] `59724873-f8c4-4822-80ee-983205b30475` — **2019-04-25-recipe**
  - _reason: The seed post details 'microgpt', a GPT implementation, which is a neural network, and the candidate post discusses 'the most common neural net mistakes' and training neural nets._

**Rejected by Gemini — tick [x] to ADD (override)**:

- [ ] `5fb0613e-263a-48b6-b400-4febd8b2264b` — **2022-03-14-lecun1989**
  - _rejected because: While both relate to neural networks, the candidate post focuses on the historical application of backpropagation for handwritten zip code recognition, which is too specific and distinct from the GPT topic of the seed._
- [ ] `b87baa3b-38fd-466f-858d-4e765e89464d` — **2015-11-20-ai**
  - _rejected because: The candidate post is a fictional story about AI and supervised learning, which is a general concept and not specifically linked to GPT models or their implementation as in the seed post._
- [ ] `1309f035-93d7-403b-a890-0540bd2eaec8` — **2018-01-20-medium**
  - _rejected because: This post is about the author's blogging platform choices and activity, which is not thematically related to the technical content of the seed post about 'microgpt'._
- [ ] `1936f8b5-9601-4767-ac52-f5e2b728af04` — **2015-10-25-selfie**
  - _rejected because: The candidate post discusses Convolutional Neural Networks for visual recognition and image manipulation, which is a different specific type of neural network and application domain than the GPT model in the seed._
- [ ] `ffb6007e-7be2-4653-b4db-b0a55dfbef92` — **2015-03-30-breaking-convnets**
  - _rejected because: The candidate post discusses Convolutional Networks and their performance in visual recognition, which is a different specific type of neural network and application domain than the GPT model in the seed._
- [ ] `979ee142-a973-42f0-95d5-26f38c03a407` — **2014-07-03-feature-learning-escapades**
  - _rejected because: The candidate post describes work on large-scale video classification using Convolutional Neural Networks, which is a different specific type of neural network and application domain than the GPT model in the seed._
- [ ] `17808433-ad82-4ea2-9fb3-98ec88aafb7e` — **2014-07-02-visualizing-top-tweeps-with-t-sne-in-Javascript**
  - _rejected because: The candidate post discusses visualizing high-dimensional data using t-SNE and other dimensionality reduction methods, which is a general data science technique not specifically related to GPT models._
- [ ] `97728ae4-a085-4bda-9176-c088e1431b73` — **2013-11-27-quantifying-hacker-news**
  - _rejected because: This post is about analyzing data from Hacker News, which is a data analysis topic and not thematically related to the technical content of the seed post about 'microgpt'._
- [ ] `919a9465-5f46-4119-88a5-ab7c783e0fa9` — **2013-11-23-chrome-extension-programming**
  - _rejected because: This post is about programming Chrome extensions, which is a software development topic and not thematically related to the technical content of the seed post about 'microgpt'._
- [ ] `d7ad6c9c-f109-4556-a211-44f8b3e0a3e5` — **2020-06-11-biohacking-lite**
  - _rejected because: This post is about biohacking and personal health, which is not thematically related to the technical content of the seed post about 'microgpt'._

---

## Seed 2/20: 2022-03-14-lecun1989
_id: `5fb0613e-263a-48b6-b400-4febd8b2264b` · mentions in graph: 10_

> <style> .post-header h1 {     font-size: 35px; } .post pre, .post code {     background-color: #fcfcfc;     font-size: 13px; /* make code smaller for this post... */ } </style>  The Yann LeCun et al. (1989) paper [Backpropagation Applied to Handwritten Zip Code Recognition](http://yann.lecun.com/exd...

**Gemini proposes these as RELATED** — tick [x] to KEEP, clear [ ] to DROP:

- [x] `1936f8b5-9601-4767-ac52-f5e2b728af04` — **2015-10-25-selfie**
  - _reason: Both posts discuss Convolutional Neural Networks, with the seed post mentioning backpropagation for handwritten zip code recognition and this post discussing their application in visual recognition tasks._
- [x] `ffb6007e-7be2-4653-b4db-b0a55dfbef92` — **2015-03-30-breaking-convnets**
  - _reason: Both posts discuss Convolutional Networks, with the seed post focusing on an early application of neural nets with backpropagation and this post discussing their effectiveness in visual recognition problems._
- [x] `979ee142-a973-42f0-95d5-26f38c03a407` — **2014-07-03-feature-learning-escapades**
  - _reason: Both posts discuss Convolutional Neural Networks, with the seed post highlighting an early application of neural nets and this post detailing large-scale video classification with CNNs._
- [x] `096ea70a-1459-47a9-b0e0-6cd4870d74f8` — **2011-04-27-manually-classifying-cifar10**
  - _reason: Both posts discuss neural network classification tasks, with the seed post focusing on handwritten zip code recognition and this post on the CIFAR-10 image classification dataset._
- [x] `58f62ce2-923d-436d-bca2-c6a5c3e18ef3` — **2015-05-21-rnn-effectiveness**
  - _reason: Both posts discuss neural networks, with the seed post focusing on an early application of backpropagation and this post on the effectiveness of Recurrent Neural Networks (RNNs) for tasks like image captioning._
- [x] `2599441e-34b5-406e-bcd3-e060026b98e5` — **2014-09-02-what-i-learned-from-competing-against-a-convnet-on-imagenet**
  - _reason: Both posts discuss Convolutional Neural Networks, with the seed post mentioning an early application of neural nets and this post detailing competition results using ConvNets on ImageNet._
- [x] `649acfbf-16a7-47ef-8a33-51f49f01b7e1` — **nntutorial**
  - _reason: Both posts discuss neural networks, with the seed post focusing on an early application of backpropagation and this post serving as a 'Hacker's guide to Neural Networks'._
- [x] `59724873-f8c4-4822-80ee-983205b30475` — **2019-04-25-recipe**
  - _reason: Both posts discuss neural networks, with the seed post focusing on an early application of backpropagation and this post on common mistakes when training neural nets._
- [x] `e6b06557-6d65-4ee6-9790-07e60f065019` — **2026-02-12-microgpt**
  - _reason: Both posts discuss neural networks, with the seed post focusing on an early application of backpropagation and this post on training and inferencing a GPT, a type of neural network._
- [x] `2e701e80-befb-4258-a53a-fb204df46181` — **2021-03-27-forward-pass**
  - _reason: Both posts discuss neural networks, with the seed post focusing on an early application of backpropagation and this post referencing GPT-3, a large language model based on neural networks._
- [x] `d14e0f1f-a3e2-450c-a23f-8b24a7689f8f` — **2012-10-22-state-of-computer-vision**
  - _reason: Both posts discuss the field of AI and Computer Vision, with the seed post focusing on an early application of neural nets and this post reflecting on the challenges and outlook for AI and Computer Vision._
- [x] `b87baa3b-38fd-466f-858d-4e765e89464d` — **2015-11-20-ai**
  - _reason: Both posts discuss AI and neural networks, with the seed post focusing on an early application of backpropagation and this post exploring the future of AI through the lens of supervised learning._

**Rejected by Gemini — tick [x] to ADD (override)**:

- [ ] `1309f035-93d7-403b-a890-0540bd2eaec8` — **2018-01-20-medium**
  - _rejected because: This post is about blogging platforms and activity, not neural networks or AI._
- [ ] `17808433-ad82-4ea2-9fb3-98ec88aafb7e` — **2014-07-02-visualizing-top-tweeps-with-t-sne-in-Javascript**
  - _rejected because: This post is about visualizing high-dimensional data using t-SNE, which is a data visualization technique, not specifically about neural networks or backpropagation._
- [ ] `97728ae4-a085-4bda-9176-c088e1431b73` — **2013-11-27-quantifying-hacker-news**
  - _rejected because: This post is about analyzing Hacker News activity, which is unrelated to neural networks or AI applications._
- [ ] `919a9465-5f46-4119-88a5-ab7c783e0fa9` — **2013-11-23-chrome-extension-programming**
  - _rejected because: This post is about programming Chrome extensions, which is unrelated to neural networks or AI._
- [ ] `d7ad6c9c-f109-4556-a211-44f8b3e0a3e5` — **2020-06-11-biohacking-lite**
  - _rejected because: This post is about personal health, exercise, diet, and nutrition, which is unrelated to neural networks or AI._
- [ ] `7010382f-4855-41b6-915f-bccebb511234` — **2014-08-03-quantifying-productivity**
  - _rejected because: This post is about quantifying personal productivity, which is unrelated to neural networks or AI._
- [ ] `8727b22c-7beb-41c3-b796-8bd15bdce3e5` — **2014-07-01-switching-to-jekyll**
  - _rejected because: This post is about switching blogging platforms from Wordpress to Jekyll, which is unrelated to neural networks or AI._
- [ ] `2fc7e67e-8e1a-4367-9606-9137d48d6af8` — **2014-04-26-datascience-weekly-interview**
  - _rejected because: This post is an interview about ConvNetJS and neural net trends, but the seed post is about a specific historical paper on backpropagation, making the link too broad without specific shared entities or techniques._
- [ ] `78d4e228-302e-469d-b654-0be5190ec4cd` — **2021-06-21-blockchain**
  - _rejected because: This post is about blockchain technology, which is unrelated to neural networks or backpropagation._
- [ ] `dd671e69-b246-4f22-8ec8-4b369b1a1102` — **2016-09-07-phd**
  - _rejected because: This post is a guide on doing well in a PhD program, which is unrelated to neural networks or AI._

---

## Seed 3/20: 2015-11-20-ai
_id: `b87baa3b-38fd-466f-858d-4e765e89464d` · mentions in graph: 10_

> <style> p {   text-align: justify; } </style>  The idea of writing a collection of short stories has been on my mind for a while. This post is my first ever half-serious attempt at a story, and what better way to kick things off than with a story on AI and what that might look like if you extrapolat...

**Gemini proposes these as RELATED** — tick [x] to KEEP, clear [ ] to DROP:

- [x] `e6b06557-6d65-4ee6-9790-07e60f065019` — **2026-02-12-microgpt**
  - _reason: The seed post discusses a story on AI and extrapolating current technology, specifically mentioning supervised learning, while this post details an AI project (microgpt) that trains and inferences a GPT, directly relating to the practical application and evolution of AI technology._
- [x] `2e701e80-befb-4258-a53a-fb204df46181` — **2021-03-27-forward-pass**
  - _reason: Both the seed post and this candidate post are short stories about AI, with the candidate explicitly mentioning GPT-3 and a Turing Test, which aligns with the seed's theme of exploring what AI might look like._
- [x] `5fb0613e-263a-48b6-b400-4febd8b2264b` — **2022-03-14-lecun1989**
  - _reason: The seed post discusses AI and the progress with scaling up supervised learning, and this post details a historically significant real-world application of a neural net trained with backpropagation, a core technique in supervised learning and AI._
- [x] `1936f8b5-9601-4767-ac52-f5e2b728af04` — **2015-10-25-selfie**
  - _reason: The seed post is about AI and extrapolating current technology, and this post discusses Convolutional Neural Networks for visual recognition, which is a specific application of AI and supervised learning mentioned in the seed._
- [x] `ffb6007e-7be2-4653-b4db-b0a55dfbef92` — **2015-03-30-breaking-convnets**
  - _reason: The seed post discusses AI and the progress with supervised learning, and this post directly addresses the performance and caveats of Convolutional Networks, a key component of modern AI and supervised learning._
- [x] `979ee142-a973-42f0-95d5-26f38c03a407` — **2014-07-03-feature-learning-escapades**
  - _reason: The seed post discusses AI and the progress with supervised learning, and this post details work on 'Large-scale Video Classification with Convolutional Neural Networks,' which is a direct application of AI and supervised learning._
- [x] `59724873-f8c4-4822-80ee-983205b30475` — **2019-04-25-recipe**
  - _reason: The seed post discusses AI and the progress with supervised learning, and this post talks about common mistakes in training neural nets, which are fundamental to AI and supervised learning approaches._
- [x] `2599441e-34b5-406e-bcd3-e060026b98e5` — **2014-09-02-what-i-learned-from-competing-against-a-convnet-on-imagenet**
  - _reason: The seed post discusses AI and the progress with supervised learning, and this post details competing against a ConvNet on ImageNet, which is a major benchmark in AI and supervised learning for computer vision._
- [x] `d14e0f1f-a3e2-450c-a23f-8b24a7689f8f` — **2012-10-22-state-of-computer-vision**
  - _reason: The seed post discusses AI and its future, and this post directly questions what it would take for a computer to understand an image like humans do, reflecting on the challenges and outlook for AI and Computer Vision._
- [x] `096ea70a-1459-47a9-b0e0-6cd4870d74f8` — **2011-04-27-manually-classifying-cifar10**
  - _reason: The seed post discusses AI and the progress with supervised learning, and this post describes the CIFAR-10 dataset and classification accuracy, which is a specific benchmark and task within supervised learning and AI._
- [x] `58f62ce2-923d-436d-bca2-c6a5c3e18ef3` — **2015-05-21-rnn-effectiveness**
  - _reason: The seed post discusses AI and the progress with supervised learning, and this post focuses on Recurrent Neural Networks (RNNs) for tasks like Image Captioning, which are advanced AI techniques and applications._
- [x] `2fc7e67e-8e1a-4367-9606-9137d48d6af8` — **2014-04-26-datascience-weekly-interview**
  - _reason: The seed post discusses AI and the progress with supervised learning, and this post mentions an interview about ConvNetJS and perspectives on neural net trends, directly relating to AI and neural network developments._
- [x] `649acfbf-16a7-47ef-8a33-51f49f01b7e1` — **nntutorial**
  - _reason: The seed post discusses AI and the progress with supervised learning, and this post is a 'Hacker's guide to Neural Networks,' which are foundational to AI and supervised learning._
- [x] `71d45412-30c7-416b-aa36-faf3f03ea868` — **2016-05-31-rl**
  - _reason: The seed post discusses AI and the progress with supervised learning, and this post introduces Reinforcement Learning (RL), which is another major paradigm within AI, indicating a broader discussion of AI approaches._

**Rejected by Gemini — tick [x] to ADD (override)**:

- [ ] `1309f035-93d7-403b-a890-0540bd2eaec8` — **2018-01-20-medium**
  - _rejected because: This post is about the author's blogging platform choices and activity, not about AI or related technical topics._
- [ ] `17808433-ad82-4ea2-9fb3-98ec88aafb7e` — **2014-07-02-visualizing-top-tweeps-with-t-sne-in-Javascript**
  - _rejected because: This post discusses visualizing high-dimensional data using t-SNE, which is a data visualization technique, not directly about AI or supervised learning as the core theme._
- [ ] `97728ae4-a085-4bda-9176-c088e1431b73` — **2013-11-27-quantifying-hacker-news**
  - _rejected because: This post is about analyzing Hacker News activity and data, which is unrelated to AI or supervised learning._
- [ ] `919a9465-5f46-4119-88a5-ab7c783e0fa9` — **2013-11-23-chrome-extension-programming**
  - _rejected because: This post is about programming Chrome extensions, which is a software development topic unrelated to AI._
- [ ] `d7ad6c9c-f109-4556-a211-44f8b3e0a3e5` — **2020-06-11-biohacking-lite**
  - _rejected because: This post is about personal health, exercise, and diet, which is not thematically related to AI._
- [ ] `7010382f-4855-41b6-915f-bccebb511234` — **2014-08-03-quantifying-productivity**
  - _rejected because: This post is about quantifying personal productivity and collecting/analyzing personal activity data, not AI._
- [ ] `8727b22c-7beb-41c3-b796-8bd15bdce3e5` — **2014-07-01-switching-to-jekyll**
  - _rejected because: This post is about switching blogging platforms from Wordpress to Jekyll, which is a technical topic unrelated to AI._
- [ ] `78d4e228-302e-469d-b654-0be5190ec4cd` — **2021-06-21-blockchain**
  - _rejected because: This post discusses blockchain technology, which is a distinct field from AI and supervised learning._
- [ ] `dd671e69-b246-4f22-8ec8-4b369b1a1102` — **2016-09-07-phd**
  - _rejected because: This post is a guide on doing well in a PhD program, which is an academic advice topic, not AI._

---

## Seed 4/20: 2018-01-20-medium
_id: `1309f035-93d7-403b-a890-0540bd2eaec8` · mentions in graph: 10_

> The current state of this blog (with the last post 2 years ago) makes it look like I've disappeared. I've certainly become less active on blogs since I've joined Tesla, but whenever I do get a chance to post something I have recently been defaulting to doing it on Medium because it is much faster an...

**Gemini proposes these as RELATED** — tick [x] to KEEP, clear [ ] to DROP:

- [x] `8727b22c-7beb-41c3-b796-8bd15bdce3e5` — **2014-07-01-switching-to-jekyll**
  - _reason: The seed post discusses the author's blogging activity and preference for Medium, while this post details the author's decision to switch from Wordpress to Jekyll for blogging, making both posts about the author's blogging platform and habits._

**Rejected by Gemini — tick [x] to ADD (override)**:

- [ ] `e6b06557-6d65-4ee6-9790-07e60f065019` — **2026-02-12-microgpt**
  - _rejected because: The candidate post is about a specific AI project (microgpt), which is not thematically related to the seed post about blogging platforms._
- [ ] `5fb0613e-263a-48b6-b400-4febd8b2264b` — **2022-03-14-lecun1989**
  - _rejected because: The candidate post discusses a historical paper on backpropagation in neural networks, which is not thematically related to the seed post about blogging platforms._
- [ ] `b87baa3b-38fd-466f-858d-4e765e89464d` — **2015-11-20-ai**
  - _rejected because: The candidate post is a short story about AI, which is not thematically related to the seed post about blogging platforms._
- [ ] `1936f8b5-9601-4767-ac52-f5e2b728af04` — **2015-10-25-selfie**
  - _rejected because: The candidate post discusses using Convolutional Neural Networks for fun applications, which is not thematically related to the seed post about blogging platforms._
- [ ] `ffb6007e-7be2-4653-b4db-b0a55dfbef92` — **2015-03-30-breaking-convnets**
  - _rejected because: The candidate post discusses the limitations and caveats of Convolutional Networks, which is not thematically related to the seed post about blogging platforms._
- [ ] `979ee142-a973-42f0-95d5-26f38c03a407` — **2014-07-03-feature-learning-escapades**
  - _rejected because: The candidate post is about the author's summer internship work on video classification with CNNs, which is not thematically related to the seed post about blogging platforms._
- [ ] `17808433-ad82-4ea2-9fb3-98ec88aafb7e` — **2014-07-02-visualizing-top-tweeps-with-t-sne-in-Javascript**
  - _rejected because: The candidate post discusses visualizing high-dimensional data using t-SNE, which is not thematically related to the seed post about blogging platforms._
- [ ] `97728ae4-a085-4bda-9176-c088e1431b73` — **2013-11-27-quantifying-hacker-news**
  - _rejected because: The candidate post is about analyzing Hacker News activity, which is not thematically related to the seed post about blogging platforms._
- [ ] `919a9465-5f46-4119-88a5-ab7c783e0fa9` — **2013-11-23-chrome-extension-programming**
  - _rejected because: The candidate post discusses hacking together Chrome extensions, which is not thematically related to the seed post about blogging platforms._
- [ ] `d7ad6c9c-f109-4556-a211-44f8b3e0a3e5` — **2020-06-11-biohacking-lite**
  - _rejected because: The candidate post is about biohacking and personal health, which is not thematically related to the seed post about blogging platforms._

---

## Seed 5/20: 2015-10-25-selfie
_id: `1936f8b5-9601-4767-ac52-f5e2b728af04` · mentions in graph: 10_

> <div class="imgcap"> <img src="/assets/selfie/teaser.jpeg" style="border:none;"> </div>  Convolutional Neural Networks are great: they recognize things, places and people in your personal photos, signs, people and lights in self-driving cars, crops, forests and traffic in aerial imagery, various ano...

**Gemini proposes these as RELATED** — tick [x] to KEEP, clear [ ] to DROP:

- [x] `ffb6007e-7be2-4653-b4db-b0a55dfbef92` — **2015-03-30-breaking-convnets**
  - _reason: Both posts discuss Convolutional Neural Networks (ConvNets) and their applications in visual recognition, with the seed post focusing on fun applications and this post on their effectiveness and limitations._
- [x] `979ee142-a973-42f0-95d5-26f38c03a407` — **2014-07-03-feature-learning-escapades**
  - _reason: Both posts discuss Convolutional Neural Networks (CNNs) and their applications in visual recognition, with the seed post mentioning their use in photos and this post detailing large-scale video classification with CNNs._
- [x] `2599441e-34b5-406e-bcd3-e060026b98e5` — **2014-09-02-what-i-learned-from-competing-against-a-convnet-on-imagenet**
  - _reason: Both posts discuss Convolutional Neural Networks (ConvNets) and their performance in visual recognition tasks, specifically mentioning ImageNet, with the seed post broadly introducing them and this post detailing a competition against a ConvNet on ImageNet._
- [x] `d14e0f1f-a3e2-450c-a23f-8b24a7689f8f` — **2012-10-22-state-of-computer-vision**
  - _reason: Both posts discuss the capabilities and limitations of AI and Computer Vision, with the seed post highlighting the power of Convolutional Neural Networks for visual recognition and this post questioning what it would take for a computer to understand an image like a human._
- [x] `096ea70a-1459-47a9-b0e0-6cd4870d74f8` — **2011-04-27-manually-classifying-cifar10**
  - _reason: Both posts discuss visual recognition and classification tasks, with the seed post mentioning Convolutional Neural Networks for recognizing things in photos and this post detailing the CIFAR-10 image classification dataset._
- [x] `649acfbf-16a7-47ef-8a33-51f49f01b7e1` — **nntutorial**
  - _reason: Both posts explicitly mention and discuss Convolutional Neural Networks (ConvNets) as a core technology, with the seed post introducing their applications and this post serving as a tutorial for neural networks, including ConvNets._

**Rejected by Gemini — tick [x] to ADD (override)**:

- [ ] `e6b06557-6d65-4ee6-9790-07e60f065019` — **2026-02-12-microgpt**
  - _rejected because: The seed post focuses on Convolutional Neural Networks for visual recognition, while this post is about training and inferencing a GPT, which is a different type of neural network primarily for language._
- [ ] `5fb0613e-263a-48b6-b400-4febd8b2264b` — **2022-03-14-lecun1989**
  - _rejected because: The seed post discusses Convolutional Neural Networks for visual recognition, while this post focuses on the historical significance of backpropagation in neural networks for handwritten zip code recognition, which is too broad a connection._
- [ ] `b87baa3b-38fd-466f-858d-4e765e89464d` — **2015-11-20-ai**
  - _rejected because: The seed post is about Convolutional Neural Networks for visual recognition, while this post is a fictional story about AI and supervised learning in a general sense, lacking specific thematic overlap._
- [ ] `1309f035-93d7-403b-a890-0540bd2eaec8` — **2018-01-20-medium**
  - _rejected because: The seed post discusses Convolutional Neural Networks, while this post is a meta-commentary on the author's blogging platform choices and activity, with no thematic link to AI or neural networks._
- [ ] `17808433-ad82-4ea2-9fb3-98ec88aafb7e` — **2014-07-02-visualizing-top-tweeps-with-t-sne-in-Javascript**
  - _rejected because: The seed post focuses on Convolutional Neural Networks for visual recognition, while this post discusses visualizing high-dimensional data using t-SNE, which is a different machine learning technique._
- [ ] `97728ae4-a085-4bda-9176-c088e1431b73` — **2013-11-27-quantifying-hacker-news**
  - _rejected because: The seed post is about Convolutional Neural Networks, while this post is about analyzing data from Hacker News, which is a completely different topic._
- [ ] `919a9465-5f46-4119-88a5-ab7c783e0fa9` — **2013-11-23-chrome-extension-programming**
  - _rejected because: The seed post discusses Convolutional Neural Networks, while this post is about programming Chrome extensions, which is unrelated._
- [ ] `d7ad6c9c-f109-4556-a211-44f8b3e0a3e5` — **2020-06-11-biohacking-lite**
  - _rejected because: The seed post discusses Convolutional Neural Networks, while this post is about personal health, exercise, and diet, which is unrelated._
- [ ] `2e701e80-befb-4258-a53a-fb204df46181` — **2021-03-27-forward-pass**
  - _rejected because: The seed post focuses on Convolutional Neural Networks for visual recognition, while this post is a short story inspired by GPT-3 and Turing tests, which relates to language models and AI philosophy rather than CNNs._
- [ ] `59724873-f8c4-4822-80ee-983205b30475` — **2019-04-25-recipe**
  - _rejected because: While this post mentions 'neural nets' and 'convnets', its focus is on common mistakes and practical advice for training them, which is a different thematic angle than the seed post's introduction to their applications for visual recognition._

---

## Seed 6/20: 2015-03-30-breaking-convnets
_id: `ffb6007e-7be2-4653-b4db-b0a55dfbef92` · mentions in graph: 10_

> You've probably heard that Convolutional Networks work very well in practice and across a wide range of visual recognition problems. You may have also read articles and papers that claim to reach a near *"human-level performance"*. There are all kinds of caveats to that (e.g. see my G+ post on [Huma...

**Gemini proposes these as RELATED** — tick [x] to KEEP, clear [ ] to DROP:

- [x] `5fb0613e-263a-48b6-b400-4febd8b2264b` — **2022-03-14-lecun1989**
  - _reason: Both posts discuss the practical application and historical significance of neural networks, specifically mentioning backpropagation and their effectiveness in visual recognition problems._
- [x] `1936f8b5-9601-4767-ac52-f5e2b728af04` — **2015-10-25-selfie**
  - _reason: Both posts explicitly discuss Convolutional Neural Networks (ConvNets) and their applications in visual recognition problems._
- [x] `979ee142-a973-42f0-95d5-26f38c03a407` — **2014-07-03-feature-learning-escapades**
  - _reason: Both posts discuss Convolutional Neural Networks (ConvNets) and their application in visual recognition, with the candidate specifically mentioning 'Large-scale Video Classification with Convolutional Neural Networks'._
- [x] `2599441e-34b5-406e-bcd3-e060026b98e5` — **2014-09-02-what-i-learned-from-competing-against-a-convnet-on-imagenet**
  - _reason: Both posts discuss Convolutional Neural Networks (ConvNets) and their performance in visual recognition challenges like ImageNet._
- [x] `096ea70a-1459-47a9-b0e0-6cd4870d74f8` — **2011-04-27-manually-classifying-cifar10**
  - _reason: Both posts discuss the performance and application of neural networks in classification tasks, with the candidate focusing on CIFAR-10 classification._
- [x] `649acfbf-16a7-47ef-8a33-51f49f01b7e1` — **nntutorial**
  - _reason: Both posts discuss neural networks, with the seed focusing on ConvNets and the candidate being a 'Hacker's guide to Neural Networks' tutorial._

**Rejected by Gemini — tick [x] to ADD (override)**:

- [ ] `e6b06557-6d65-4ee6-9790-07e60f065019` — **2026-02-12-microgpt**
  - _rejected because: The seed post focuses on Convolutional Networks for visual recognition, while the candidate discusses training and inferencing a GPT, which is a different type of neural network and application._
- [ ] `b87baa3b-38fd-466f-858d-4e765e89464d` — **2015-11-20-ai**
  - _rejected because: The seed post discusses Convolutional Networks, while the candidate is a short story about AI in general, without a specific technical link._
- [ ] `1309f035-93d7-403b-a890-0540bd2eaec8` — **2018-01-20-medium**
  - _rejected because: The candidate post is about the author's blogging platform choices and activity, not about Convolutional Networks or visual recognition._
- [ ] `17808433-ad82-4ea2-9fb3-98ec88aafb7e` — **2014-07-02-visualizing-top-tweeps-with-t-sne-in-Javascript**
  - _rejected because: The seed post is about Convolutional Networks, while the candidate discusses visualizing high-dimensional data using t-SNE, which is a different machine learning technique._
- [ ] `97728ae4-a085-4bda-9176-c088e1431b73` — **2013-11-27-quantifying-hacker-news**
  - _rejected because: The candidate post is about analyzing Hacker News activity, which is unrelated to Convolutional Networks or visual recognition._
- [ ] `919a9465-5f46-4119-88a5-ab7c783e0fa9` — **2013-11-23-chrome-extension-programming**
  - _rejected because: The candidate post is about Chrome extension programming, which is unrelated to Convolutional Networks or visual recognition._
- [ ] `d7ad6c9c-f109-4556-a211-44f8b3e0a3e5` — **2020-06-11-biohacking-lite**
  - _rejected because: The candidate post is about biohacking and personal health, which is unrelated to Convolutional Networks or visual recognition._
- [ ] `2e701e80-befb-4258-a53a-fb204df46181` — **2021-03-27-forward-pass**
  - _rejected because: The seed post focuses on Convolutional Networks, while the candidate is a short story inspired by GPT-3, a different type of neural network and application._
- [ ] `59724873-f8c4-4822-80ee-983205b30475` — **2019-04-25-recipe**
  - _rejected because: While both discuss neural nets, the candidate focuses on common mistakes in training neural nets generally, without a specific thematic link to Convolutional Networks or visual recognition as the core topic._
- [ ] `7010382f-4855-41b6-915f-bccebb511234` — **2014-08-03-quantifying-productivity**
  - _rejected because: The candidate post is about quantifying personal productivity, which is unrelated to Convolutional Networks or visual recognition._

---

## Seed 7/20: 2014-07-03-feature-learning-escapades
_id: `979ee142-a973-42f0-95d5-26f38c03a407` · mentions in graph: 10_

> My summer internship work at Google has turned into a CVPR 2014 Oral titled  **"Large-scale Video Classification with Convolutional Neural Networks"** [(project page)](http://cs.stanford.edu/people/karpathy/deepvideo/). Politically correct, professional, and carefully crafted scientific exposition i...

**Gemini proposes these as RELATED** — tick [x] to KEEP, clear [ ] to DROP:

- [x] `5fb0613e-263a-48b6-b400-4febd8b2264b` — **2022-03-14-lecun1989**
  - _reason: Both posts discuss the application and historical significance of neural networks, with the seed post focusing on Convolutional Neural Networks for video classification and this post on backpropagation applied to handwritten zip code recognition._
- [x] `1936f8b5-9601-4767-ac52-f5e2b728af04` — **2015-10-25-selfie**
  - _reason: Both posts explicitly discuss Convolutional Neural Networks (ConvNets) and their applications, with the seed post on video classification and this post on visual recognition tasks like selfies._
- [x] `ffb6007e-7be2-4653-b4db-b0a55dfbef92` — **2015-03-30-breaking-convnets**
  - _reason: Both posts discuss Convolutional Networks and their performance in visual recognition problems, with the seed post detailing a specific application and this post discussing their general effectiveness and limitations._
- [x] `2599441e-34b5-406e-bcd3-e060026b98e5` — **2014-09-02-what-i-learned-from-competing-against-a-convnet-on-imagenet**
  - _reason: Both posts discuss the ImageNet Large Scale Visual Recognition Challenge (ILSVRC) and the role of ConvNets in computer vision, with the seed post mentioning a CVPR oral presentation on video classification and this post detailing lessons learned from competing in ILSVRC._
- [x] `d14e0f1f-a3e2-450c-a23f-8b24a7689f8f` — **2012-10-22-state-of-computer-vision**
  - _reason: Both posts discuss the field of Computer Vision and the capabilities of AI, with the seed post detailing a specific application of Convolutional Neural Networks and this post reflecting on the broader challenges in computer vision._
- [x] `096ea70a-1459-47a9-b0e0-6cd4870d74f8` — **2011-04-27-manually-classifying-cifar10**
  - _reason: Both posts discuss image classification using neural networks, with the seed post focusing on large-scale video classification with Convolutional Neural Networks and this post on classifying CIFAR-10 images._
- [x] `58f62ce2-923d-436d-bca2-c6a5c3e18ef3` — **2015-05-21-rnn-effectiveness**
  - _reason: Both posts discuss types of neural networks and their applications, with the seed post focusing on Convolutional Neural Networks for video classification and this post on Recurrent Neural Networks for image captioning._
- [x] `2fc7e67e-8e1a-4367-9606-9137d48d6af8` — **2014-04-26-datascience-weekly-interview**
  - _reason: Both posts discuss neural networks and their trends, with the seed post detailing an internship project on Convolutional Neural Networks and this post being an interview about ConvNetJS and neural net trends._
- [x] `649acfbf-16a7-47ef-8a33-51f49f01b7e1` — **nntutorial**
  - _reason: Both posts discuss neural networks, with the seed post detailing a project on Convolutional Neural Networks and this post being a 'Hacker's guide to Neural Networks' tutorial._
- [x] `59724873-f8c4-4822-80ee-983205b30475` — **2019-04-25-recipe**
  - _reason: Both posts discuss neural networks, with the seed post detailing a project on Convolutional Neural Networks and this post discussing common mistakes and the practical application of training neural nets._

**Rejected by Gemini — tick [x] to ADD (override)**:

- [ ] `e6b06557-6d65-4ee6-9790-07e60f065019` — **2026-02-12-microgpt**
  - _rejected because: The seed post focuses on Convolutional Neural Networks for video classification, while this post introduces 'microgpt', a different type of neural network (GPT) for text generation, without a clear thematic overlap beyond the broad field of AI._
- [ ] `b87baa3b-38fd-466f-858d-4e765e89464d` — **2015-11-20-ai**
  - _rejected because: The seed post discusses a specific technical project involving Convolutional Neural Networks, while this post is a short story about AI, which is too broad to be thematically related._
- [ ] `1309f035-93d7-403b-a890-0540bd2eaec8` — **2018-01-20-medium**
  - _rejected because: The seed post is about a specific technical project, while this post is about the author's blogging platform choices and activity, which is not thematically related._
- [ ] `17808433-ad82-4ea2-9fb3-98ec88aafb7e` — **2014-07-02-visualizing-top-tweeps-with-t-sne-in-Javascript**
  - _rejected because: The seed post is about Convolutional Neural Networks for video classification, while this post is about visualizing high-dimensional data using t-SNE, which is a different technical focus._
- [ ] `97728ae4-a085-4bda-9176-c088e1431b73` — **2013-11-27-quantifying-hacker-news**
  - _rejected because: The seed post is about a specific technical project in deep learning, while this post is about data analysis of Hacker News activity, which is not thematically related._
- [ ] `919a9465-5f46-4119-88a5-ab7c783e0fa9` — **2013-11-23-chrome-extension-programming**
  - _rejected because: The seed post is about a specific technical project in deep learning, while this post is about programming Chrome extensions, which is not thematically related._
- [ ] `d7ad6c9c-f109-4556-a211-44f8b3e0a3e5` — **2020-06-11-biohacking-lite**
  - _rejected because: The seed post is about a specific technical project in deep learning, while this post is about personal health and biohacking, which is not thematically related._
- [ ] `2e701e80-befb-4258-a53a-fb204df46181` — **2021-03-27-forward-pass**
  - _rejected because: The seed post focuses on Convolutional Neural Networks for video classification, while this post is a short story inspired by GPT-3, a different type of AI model, without a clear thematic overlap beyond the broad field of AI._
- [ ] `7010382f-4855-41b6-915f-bccebb511234` — **2014-08-03-quantifying-productivity**
  - _rejected because: The seed post is about a specific technical project in deep learning, while this post is about quantifying personal productivity, which is not thematically related._
- [ ] `8727b22c-7beb-41c3-b796-8bd15bdce3e5` — **2014-07-01-switching-to-jekyll**
  - _rejected because: The seed post is about a specific technical project in deep learning, while this post is about switching blogging platforms, which is not thematically related._

---

## Seed 8/20: 2014-07-02-visualizing-top-tweeps-with-t-sne-in-Javascript
_id: `17808433-ad82-4ea2-9fb3-98ec88aafb7e` · mentions in graph: 10_

> <img src="/assets/tsne_preview.jpeg" width="100%">  I was recently looking into various ways of embedding unlabeled, high-dimensional data in 2 dimensions for visualization. A wide variety of methods have been proposed for this task. [This Review paper](http://homepage.tudelft.nl/19j49/Matlab_Toolbo...

**Gemini proposes these as RELATED** — tick [x] to KEEP, clear [ ] to DROP:

- [x] `979ee142-a973-42f0-95d5-26f38c03a407` — **2014-07-03-feature-learning-escapades**
  - _reason: Both the seed post and this candidate post discuss visualizing and analyzing data, with the seed focusing on high-dimensional data visualization and this post on visualizing Hacker News stories and activity._
- [x] `7010382f-4855-41b6-915f-bccebb511234` — **2014-08-03-quantifying-productivity**
  - _reason: Both the seed post and this candidate post discuss collecting, analyzing, and interpreting data, with the seed focusing on high-dimensional data visualization and this post on quantifying personal productivity._

**Rejected by Gemini — tick [x] to ADD (override)**:

- [ ] `e6b06557-6d65-4ee6-9790-07e60f065019` — **2026-02-12-microgpt**
  - _rejected because: The candidate post is about training and inferencing a GPT model, which is a specific application of neural networks, while the seed post is about general high-dimensional data visualization techniques._
- [ ] `5fb0613e-263a-48b6-b400-4febd8b2264b` — **2022-03-14-lecun1989**
  - _rejected because: The candidate post discusses the historical significance of backpropagation in neural networks, which is a specific machine learning algorithm, while the seed post is about general high-dimensional data visualization._
- [ ] `b87baa3b-38fd-466f-858d-4e765e89464d` — **2015-11-20-ai**
  - _rejected because: The candidate post is a fictional story about AI and supervised learning, which is a narrative piece, while the seed post is a technical discussion of data visualization methods._
- [ ] `1309f035-93d7-403b-a890-0540bd2eaec8` — **2018-01-20-medium**
  - _rejected because: The candidate post discusses the author's blogging platform choices and activity, which is a meta-discussion about blogging, not a technical topic related to data visualization._
- [ ] `1936f8b5-9601-4767-ac52-f5e2b728af04` — **2015-10-25-selfie**
  - _rejected because: The candidate post discusses using Convolutional Neural Networks for visual recognition and amusement, which is a specific application of deep learning, while the seed post is about general high-dimensional data visualization._
- [ ] `ffb6007e-7be2-4653-b4db-b0a55dfbef92` — **2015-03-30-breaking-convnets**
  - _rejected because: The candidate post discusses the performance and caveats of Convolutional Networks in visual recognition, which is a specific machine learning model, while the seed post is about general high-dimensional data visualization._
- [ ] `97728ae4-a085-4bda-9176-c088e1431b73` — **2013-11-27-quantifying-hacker-news**
  - _rejected because: The candidate post discusses the author's summer internship work on large-scale video classification with Convolutional Neural Networks, which is a specific application of deep learning, while the seed post is about general high-dimensional data visualization._
- [ ] `919a9465-5f46-4119-88a5-ab7c783e0fa9` — **2013-11-23-chrome-extension-programming**
  - _rejected because: The candidate post discusses programming Chrome extensions, which is a software development topic, not related to data visualization or dimensionality reduction._
- [ ] `d7ad6c9c-f109-4556-a211-44f8b3e0a3e5` — **2020-06-11-biohacking-lite**
  - _rejected because: The candidate post discusses personal health, exercise, and diet, which is a biohacking topic, unrelated to data visualization or machine learning._
- [ ] `2e701e80-befb-4258-a53a-fb204df46181` — **2021-03-27-forward-pass**
  - _rejected because: The candidate post is a short story inspired by GPT-3 and the Turing Test, which is a narrative piece about AI, not a technical discussion of data visualization methods._

---

## Seed 9/20: 2013-11-27-quantifying-hacker-news
_id: `97728ae4-a085-4bda-9176-c088e1431b73` · mentions in graph: 10_

> ### Quantifying Hacker News I thought it would be fun to analyze the activity on one of my favorite sources of interesting links and information, <a href="https://news.ycombinator.com/">Hacker News</a>. My source of data is a script I've set up some time in August that downloads HN (the Front page a...

**Gemini proposes these as RELATED** — tick [x] to KEEP, clear [ ] to DROP:

- [x] `7010382f-4855-41b6-915f-bccebb511234` — **2014-08-03-quantifying-productivity**
  - _reason: Both the seed post and this candidate post focus on 'quantifying' and 'analyzing activity' or 'productivity' using collected data, indicating a shared theme of self-quantification and data analysis of personal or online behavior._
- [x] `919a9465-5f46-4119-88a5-ab7c783e0fa9` — **2013-11-23-chrome-extension-programming**
  - _reason: The seed post analyzes Hacker News, and this candidate post discusses 'hacking together custom browser extensions in Chrome' to 'customize my favorite websites', suggesting a shared interest in web customization and interaction with online platforms, potentially including Hacker News._

**Rejected by Gemini — tick [x] to ADD (override)**:

- [ ] `e6b06557-6d65-4ee6-9790-07e60f065019` — **2026-02-12-microgpt**
  - _rejected because: The candidate post is about training and inferencing a GPT model, which is a specific topic in AI, unrelated to quantifying Hacker News activity._
- [ ] `5fb0613e-263a-48b6-b400-4febd8b2264b` — **2022-03-14-lecun1989**
  - _rejected because: This post discusses a historical paper on backpropagation and neural networks, which is a specific AI/ML topic not related to analyzing Hacker News._
- [ ] `b87baa3b-38fd-466f-858d-4e765e89464d` — **2015-11-20-ai**
  - _rejected because: This post is a short story about AI and supervised learning, which is a creative piece on a specific AI topic, not related to data analysis of Hacker News._
- [ ] `1309f035-93d7-403b-a890-0540bd2eaec8` — **2018-01-20-medium**
  - _rejected because: This post discusses the author's blogging platform choices (Medium vs. personal blog), which is a meta-discussion about publishing, not related to quantifying Hacker News._
- [ ] `1936f8b5-9601-4767-ac52-f5e2b728af04` — **2015-10-25-selfie**
  - _rejected because: This post is about using Convolutional Neural Networks for visual recognition and amusement, a specific application of AI, unrelated to the seed post's topic._
- [ ] `ffb6007e-7be2-4653-b4db-b0a55dfbef92` — **2015-03-30-breaking-convnets**
  - _rejected because: This post discusses the effectiveness and caveats of Convolutional Networks in visual recognition, a specific AI/ML topic, not related to analyzing Hacker News._
- [ ] `979ee142-a973-42f0-95d5-26f38c03a407` — **2014-07-03-feature-learning-escapades**
  - _rejected because: This post is about large-scale video classification with Convolutional Neural Networks, a specific AI/ML research topic, not related to quantifying Hacker News._
- [ ] `17808433-ad82-4ea2-9fb3-98ec88aafb7e` — **2014-07-02-visualizing-top-tweeps-with-t-sne-in-Javascript**
  - _rejected because: This post is about visualizing high-dimensional data using t-SNE, a data visualization technique, which is too general to be specifically related to quantifying Hacker News._
- [ ] `d7ad6c9c-f109-4556-a211-44f8b3e0a3e5` — **2020-06-11-biohacking-lite**
  - _rejected because: This post is about biohacking and personal health, which is a completely different thematic area from analyzing Hacker News data._
- [ ] `2e701e80-befb-4258-a53a-fb204df46181` — **2021-03-27-forward-pass**
  - _rejected because: This post is a short story inspired by GPT-3 and Turing tests, focusing on AI, which is not thematically linked to quantifying Hacker News._

---

## Seed 10/20: 2013-11-23-chrome-extension-programming
_id: `919a9465-5f46-4119-88a5-ab7c783e0fa9` · mentions in graph: 10_

> ### Extension Hacking I wanted to share a few examples of a powerful skill that I've been gradually picking up over the last year. It is simply the ability to quickly hack together custom browser extensions in Chrome and using them to customize my favorite websites. Writing extensions is very fast: ...

**Gemini proposes these as RELATED** — tick [x] to KEEP, clear [ ] to DROP:

- [x] `97728ae4-a085-4bda-9176-c088e1431b73` — **2013-11-27-quantifying-hacker-news**
  - _reason: This post describes hacking together a script to analyze Hacker News, which is thematically similar to the seed post's focus on quickly hacking together custom browser extensions to customize websites._
- [x] `7010382f-4855-41b6-915f-bccebb511234` — **2014-08-03-quantifying-productivity**
  - _reason: This post discusses writing a script to collect and analyze personal productivity data, which aligns with the seed post's theme of quickly hacking together custom tools for personal use and customization._

**Rejected by Gemini — tick [x] to ADD (override)**:

- [ ] `e6b06557-6d65-4ee6-9790-07e60f065019` — **2026-02-12-microgpt**
  - _rejected because: This post is about building a GPT model in Python, which is a specific AI/ML topic not related to browser extension programming or general 'hacking' in the seed post's context._
- [ ] `5fb0613e-263a-48b6-b400-4febd8b2464b` — **(unknown id)**
  - _rejected because: This post discusses a historical paper on backpropagation in neural networks, which is a specific AI/ML topic unrelated to browser extension programming._
- [ ] `b87baa3b-38fd-466f-858d-4e765e89464d` — **2015-11-20-ai**
  - _rejected because: This post is a short story about AI, which is a broad topic not specifically linked to browser extension programming._
- [ ] `1309f035-93d7-403b-a890-0540bd2eaec8` — **2018-01-20-medium**
  - _rejected because: This post discusses the author's blogging platform choices (Medium vs. personal blog), which is not related to browser extension programming._
- [ ] `1936f8b5-9601-4767-ac52-f5e2b728af04` — **2015-10-25-selfie**
  - _rejected because: This post is about using Convolutional Neural Networks for visual recognition and amusement, a specific AI/ML application unrelated to browser extension programming._
- [ ] `ffb6007e-7be2-4653-b4db-b0a55dfbef92` — **2015-03-30-breaking-convnets**
  - _rejected because: This post discusses the limitations and caveats of Convolutional Networks in visual recognition, a specific AI/ML topic unrelated to browser extension programming._
- [ ] `979ee142-a973-42f0-95d5-26f38c03a407` — **2014-07-03-feature-learning-escapades**
  - _rejected because: This post is about large-scale video classification with Convolutional Neural Networks, a specific AI/ML research topic unrelated to browser extension programming._
- [ ] `17808433-ad82-4ea2-9fb3-98ec88aafb7e` — **2014-07-02-visualizing-top-tweeps-with-t-sne-in-Javascript**
  - _rejected because: This post discusses visualizing high-dimensional data using t-SNE in Javascript, which is a data visualization and machine learning technique, not directly related to browser extension programming as a general 'hacking' skill._
- [ ] `d7ad6c9c-f109-4556-a211-44f8b3e0a3e5` — **2020-06-11-biohacking-lite**
  - _rejected because: This post is about biohacking and personal health, which is a completely different thematic area from browser extension programming._
- [ ] `2e701e80-befb-4258-a53a-fb204df46181` — **2021-03-27-forward-pass**
  - _rejected because: This post is a short story inspired by GPT-3 and Turing tests, which falls under AI/ML narrative and is not related to browser extension programming._

---

## Seed 11/20: 2020-06-11-biohacking-lite
_id: `d7ad6c9c-f109-4556-a211-44f8b3e0a3e5` · mentions in graph: 9_

> Throughout my life I never paid too much attention to health, exercise, diet or nutrition. I knew that you're supposed to get some exercise and eat vegetables or something, but it stopped at that ("mom said"-) level of abstraction. I also knew that I can probably get away with some ignorance while I...

**Gemini proposes these as RELATED** — tick [x] to KEEP, clear [ ] to DROP:

_(Gemini found no related posts — leave empty, or add manually at bottom)_


**Rejected by Gemini — tick [x] to ADD (override)**:

- [ ] `e6b06557-6d65-4ee6-9790-07e60f065019` — **2026-02-12-microgpt**
  - _rejected because: The candidate post is about a GPT project and its implementation, which is unrelated to the seed post's topic of personal health and biohacking._
- [ ] `5fb0613e-263a-48b6-b400-4febd8b2264b` — **2022-03-14-lecun1989**
  - _rejected because: The candidate post discusses a historical paper on neural networks and backpropagation, which is not related to the seed post's focus on personal health and lifestyle changes._
- [ ] `b87baa3b-38fd-466f-858d-4e765e89464d` — **2015-11-20-ai**
  - _rejected because: The candidate post is a short story about AI, which has no thematic connection to the seed post's discussion of health, exercise, and diet._
- [ ] `1309f035-93d7-403b-a890-0540bd2eaec8` — **2018-01-20-medium**
  - _rejected because: The candidate post is about the author's blogging platform choices and activity, which is not thematically related to the seed post's topic of biohacking and health._
- [ ] `1936f8b5-9601-4767-ac52-f5e2b728af04` — **2015-10-25-selfie**
  - _rejected because: The candidate post discusses Convolutional Neural Networks and their applications in visual recognition, which is unrelated to the seed post's theme of personal health and biohacking._
- [ ] `ffb6007e-7be2-4653-b4db-b0a55dfbef92` — **2015-03-30-breaking-convnets**
  - _rejected because: The candidate post is about the effectiveness and limitations of Convolutional Networks in visual recognition, which is not related to the seed post's topic of personal health and lifestyle._
- [ ] `979ee142-a973-42f0-95d5-26f38c03a407` — **2014-07-03-feature-learning-escapades**
  - _rejected because: The candidate post describes an internship project on large-scale video classification with Convolutional Neural Networks, which is unrelated to the seed post's theme of personal health and biohacking._
- [ ] `17808433-ad82-4ea2-9fb3-98ec88aafb7e` — **2014-07-02-visualizing-top-tweeps-with-t-sne-in-Javascript**
  - _rejected because: The candidate post discusses visualizing high-dimensional data using t-SNE and other methods, which is a technical topic unrelated to the seed post's focus on personal health._
- [ ] `97728ae4-a085-4bda-9176-c088e1431b73` — **2013-11-27-quantifying-hacker-news**
  - _rejected because: The candidate post is about analyzing Hacker News activity and popular topics, which is unrelated to the seed post's theme of personal health and biohacking._
- [ ] `919a9465-5f46-4119-88a5-ab7c783e0fa9` — **2013-11-23-chrome-extension-programming**
  - _rejected because: The candidate post discusses programming Chrome extensions, which is a technical topic unrelated to the seed post's focus on personal health and lifestyle changes._

---

## Seed 12/20: 2021-03-27-forward-pass
_id: `2e701e80-befb-4258-a53a-fb204df46181` · mentions in graph: 9_

> <style> p {   text-align: justify; } .post pre, .post code {     border: none;     background-color: #eee; }  </style>   The inspiration for this short story came to me while reading Kevin Lacker's [Giving GPT-3 a Turing Test](https://lacker.io/ai/2020/07/06/giving-gpt-3-a-turing-test.html). It is p...

**Gemini proposes these as RELATED** — tick [x] to KEEP, clear [ ] to DROP:

- [x] `e6b06557-6d65-4ee6-9790-07e60f065019` — **2026-02-12-microgpt**
  - _reason: The seed post explicitly references 'GPT-3' and 'Turing Test' in the abstract, and this candidate post is about 'microgpt', a smaller version of GPT, making it directly related to the GPT family of models._
- [x] `b87baa3b-38fd-466f-858d-4e765e89464d` — **2015-11-20-ai**
  - _reason: The seed post is a short story inspired by GPT-3 and a Turing Test, indicating a focus on AI and its implications, which directly aligns with this candidate post's theme of a short story on AI and its future._

**Rejected by Gemini — tick [x] to ADD (override)**:

- [ ] `5fb0613e-263a-48b6-b400-4febd8b2264b` — **2022-03-14-lecun1989**
  - _rejected because: The candidate post discusses the historical significance of backpropagation in neural networks, which is a general AI concept, but lacks a specific thematic link to GPT-3 or Turing tests mentioned in the seed._
- [ ] `1309f035-93d7-403b-a890-0540bd2eaec8` — **2018-01-20-medium**
  - _rejected because: The candidate post is about the author's blogging platform choices (Medium vs. personal blog) and does not discuss AI, GPT-3, or Turing tests._
- [ ] `1936f8b5-9601-4767-ac52-f5e2b728af04` — **2015-10-25-selfie**
  - _rejected because: The candidate post discusses Convolutional Neural Networks for visual recognition and 'selfies', which is a different specific AI application than the GPT-3 and Turing Test focus of the seed._
- [ ] `ffb6007e-7be2-4653-b4db-b0a55dfbef92` — **2015-03-30-breaking-convnets**
  - _rejected because: The candidate post discusses the limitations and performance of Convolutional Networks in visual recognition, which is a different specific AI topic than the GPT-3 and Turing Test focus of the seed._
- [ ] `979ee142-a973-42f0-95d5-26f38c03a407` — **2014-07-03-feature-learning-escapades**
  - _rejected because: The candidate post discusses large-scale video classification with Convolutional Neural Networks, which is a specific application of AI distinct from the GPT-3 and Turing Test theme of the seed._
- [ ] `17808433-ad82-4ea2-9fb3-98ec88aafb7e` — **2014-07-02-visualizing-top-tweeps-with-t-sne-in-Javascript**
  - _rejected because: The candidate post focuses on visualizing high-dimensional data using t-SNE and other dimensionality reduction methods, which is a general data science technique not specifically linked to GPT-3 or Turing tests._
- [ ] `97728ae4-a085-4bda-9176-c088e1431b73` — **2013-11-27-quantifying-hacker-news**
  - _rejected because: The candidate post is about quantifying and analyzing data from Hacker News, which is a data analysis topic unrelated to AI models like GPT-3 or Turing tests._
- [ ] `919a9465-5f46-4119-88a5-ab7c783e0fa9` — **2013-11-23-chrome-extension-programming**
  - _rejected because: The candidate post discusses programming Chrome extensions, which is a software development topic unrelated to AI models like GPT-3 or Turing tests._
- [ ] `d7ad6c9c-f109-4556-a211-44f8b3e0a3e5` — **2020-06-11-biohacking-lite**
  - _rejected because: The candidate post is about personal health, exercise, diet, and nutrition ('biohacking'), which is entirely unrelated to AI, GPT-3, or Turing tests._
- [ ] `59724873-f8c4-4822-80ee-983205b30475` — **2019-04-25-recipe**
  - _rejected because: The candidate post discusses common mistakes in training neural networks, a general topic in machine learning practice, but lacks a specific connection to GPT-3 or Turing tests._

---

## Seed 13/20: 2019-04-25-recipe
_id: `59724873-f8c4-4822-80ee-983205b30475` · mentions in graph: 9_

> Some few weeks ago I [posted](https://twitter.com/karpathy/status/1013244313327681536?lang=en) a tweet on "the most common neural net mistakes", listing a few common gotchas related to training neural nets. The tweet got quite a bit more engagement than I anticipated (including a [webinar](https://w...

**Gemini proposes these as RELATED** — tick [x] to KEEP, clear [ ] to DROP:

- [x] `e6b06557-6d65-4ee6-9790-07e60f065019` — **2026-02-12-microgpt**
  - _reason: Both posts discuss neural networks, with the seed post mentioning common neural net mistakes and the candidate post detailing the training and inference of a GPT, a type of neural network._
- [x] `5fb0613e-263a-48b6-b400-4febd8b2264b` — **2022-03-14-lecun1989**
  - _reason: Both posts discuss neural networks, with the seed post mentioning common neural net mistakes and the candidate post discussing a historical application of a neural net trained with backpropagation._
- [x] `1936f8b5-9601-4767-ac52-f5e2b728af04` — **2015-10-25-selfie**
  - _reason: Both posts discuss neural networks, with the seed post mentioning common neural net mistakes and the candidate post focusing on Convolutional Neural Networks for visual recognition._
- [x] `ffb6007e-7be2-4653-b4db-b0a55dfbef92` — **2015-03-30-breaking-convnets**
  - _reason: Both posts discuss neural networks, with the seed post mentioning common neural net mistakes and the candidate post discussing the effectiveness of Convolutional Networks in visual recognition._
- [x] `979ee142-a973-42f0-95d5-26f38c03a407` — **2014-07-03-feature-learning-escapades**
  - _reason: Both posts discuss neural networks, with the seed post mentioning common neural net mistakes and the candidate post detailing work on Large-scale Video Classification with Convolutional Neural Networks._
- [x] `2e701e80-befb-4258-a53a-fb204df46181` — **2021-03-27-forward-pass**
  - _reason: Both posts discuss neural networks, with the seed post mentioning common neural net mistakes and the candidate post referencing GPT-3, a specific neural network model._
- [x] `2599441e-34b5-406e-bcd3-e060026b98e5` — **2014-09-02-what-i-learned-from-competing-against-a-convnet-on-imagenet**
  - _reason: Both posts discuss neural networks, with the seed post mentioning common neural net mistakes and the candidate post discussing competing against a ConvNet on ImageNet._
- [x] `d14e0f1f-a3e2-450c-a23f-8b24a7689f8f` — **2012-10-22-state-of-computer-vision**
  - _reason: Both posts discuss neural networks and AI, with the seed post mentioning common neural net mistakes and the candidate post discussing the challenges for a computer to understand images like humans do._
- [x] `096ea70a-1459-47a9-b0e0-6cd4870d74f8` — **2011-04-27-manually-classifying-cifar10**
  - _reason: Both posts discuss neural networks, with the seed post mentioning common neural net mistakes and the candidate post discussing classifying images using CIFAR-10, a common dataset for neural network evaluation._
- [x] `58f62ce2-923d-436d-bca2-c6a5c3e18ef3` — **2015-05-21-rnn-effectiveness**
  - _reason: Both posts discuss neural networks, with the seed post mentioning common neural net mistakes and the candidate post focusing on the effectiveness of Recurrent Neural Networks (RNNs)._
- [x] `2fc7e67e-8e1a-4367-9606-9137d48d6af8` — **2014-04-26-datascience-weekly-interview**
  - _reason: Both posts discuss neural networks, with the seed post mentioning common neural net mistakes and the candidate post discussing an interview about ConvNetJS and neural net trends._
- [x] `649acfbf-16a7-47ef-8a33-51f49f01b7e1` — **nntutorial**
  - _reason: Both posts discuss neural networks, with the seed post mentioning common neural net mistakes and the candidate post being a 'Hacker's guide to Neural Networks'._
- [x] `71d45412-30c7-416b-aa36-faf3f03ea868` — **2016-05-31-rl**
  - _reason: Both posts discuss neural networks, with the seed post mentioning common neural net mistakes and the candidate post focusing on Reinforcement Learning (RL), a field that often uses neural networks._

**Rejected by Gemini — tick [x] to ADD (override)**:

- [ ] `b87baa3b-38fd-466f-858d-4e765e89464d` — **2015-11-20-ai**
  - _rejected because: The candidate post is a short story about AI, which is too general to be thematically linked to the seed post's specific discussion of neural net mistakes._
- [ ] `1309f035-93d7-403b-a890-0540bd2eaec8` — **2018-01-20-medium**
  - _rejected because: The candidate post discusses the author's blogging platform choices and activity, which is not thematically related to neural net mistakes._
- [ ] `17808433-ad82-4ea2-9fb3-98ec88aafb7e` — **2014-07-02-visualizing-top-tweeps-with-t-sne-in-Javascript**
  - _rejected because: The candidate post discusses visualizing high-dimensional data with t-SNE, which is a general data visualization technique and not specifically linked to neural network mistakes._
- [ ] `97728ae4-a085-4bda-9176-c088e1431b73` — **2013-11-27-quantifying-hacker-news**
  - _rejected because: The candidate post is about quantifying Hacker News activity, which is unrelated to neural network mistakes._
- [ ] `919a9465-5f46-4119-88a5-ab7c783e0fa9` — **2013-11-23-chrome-extension-programming**
  - _rejected because: The candidate post discusses programming Chrome extensions, which has no thematic link to neural network mistakes._
- [ ] `d7ad6c9c-f109-4556-a211-44f8b3e0a3e5` — **2020-06-11-biohacking-lite**
  - _rejected because: The candidate post discusses personal health and biohacking, which is not thematically related to neural network mistakes._
- [ ] `7010382f-4855-41b6-915f-bccebb511234` — **2014-08-03-quantifying-productivity**
  - _rejected because: The candidate post is about quantifying personal productivity, which is not thematically related to neural network mistakes._
- [ ] `8727b22c-7beb-41c3-b796-8bd15bdce3e5` — **2014-07-01-switching-to-jekyll**
  - _rejected because: The candidate post discusses switching blogging platforms from Wordpress to Jekyll, which is not thematically related to neural network mistakes._
- [ ] `78d4e228-302e-469d-b654-0be5190ec4cd` — **2021-06-21-blockchain**
  - _rejected because: The candidate post discusses blockchain technology, which is not thematically related to neural network mistakes._
- [ ] `dd671e69-b246-4f22-8ec8-4b369b1a1102` — **2016-09-07-phd**
  - _rejected because: The candidate post is a guide on doing well in a PhD, which is not thematically related to neural network mistakes._

---

## Seed 14/20: 2014-09-02-what-i-learned-from-competing-against-a-convnet-on-imagenet
_id: `2599441e-34b5-406e-bcd3-e060026b98e5` · mentions in graph: 9_

> The results of the 2014 [ImageNet Large Scale Visual Recognition Challenge](http://www.image-net.org/challenges/LSVRC/2014/) (ILSVRC) were [published](http://www.image-net.org/challenges/LSVRC/2014/results) a few days ago. The New York Times [wrote about it](http://bits.blogs.nytimes.com/2014/08/18/...

**Gemini proposes these as RELATED** — tick [x] to KEEP, clear [ ] to DROP:

- [x] `ffb6007e-7be2-4653-b4db-b0a55dfbef92` — **2015-03-30-breaking-convnets**
  - _reason: Both posts discuss Convolutional Networks and their performance in visual recognition problems, with the seed post specifically mentioning the ImageNet challenge and this post discussing their general effectiveness and 'human-level performance'._
- [x] `1936f8b5-9601-4767-ac52-f5e2b728af04` — **2015-10-25-selfie**
  - _reason: Both posts discuss Convolutional Neural Networks and their applications in visual recognition, with the seed post focusing on the ImageNet challenge and this post on various recognition tasks including personal photos and self-driving cars._
- [x] `979ee142-a973-42f0-95d5-26f38c03a407` — **2014-07-03-feature-learning-escapades**
  - _reason: Both posts discuss Convolutional Neural Networks (ConvNets) in the context of large-scale visual recognition, with the seed post focusing on ImageNet and this post on large-scale video classification._
- [x] `096ea70a-1459-47a9-b0e0-6cd4870d74f8` — **2011-04-27-manually-classifying-cifar10**
  - _reason: Both posts discuss image classification datasets and challenges, with the seed post focusing on ImageNet and this post on CIFAR-10, both of which are benchmarks for computer vision tasks._
- [x] `d14e0f1f-a3e2-450c-a23f-8b24a7689f8f` — **2012-10-22-state-of-computer-vision**
  - _reason: Both posts discuss the state and challenges of Computer Vision and AI, with the seed post mentioning the ImageNet challenge as a benchmark and this post reflecting on what it would take for computers to understand images like humans._
- [x] `5fb0613e-263a-48b6-b400-4febd8b2264b` — **2022-03-14-lecun1989**
  - _reason: Both posts discuss neural networks and their applications in recognition tasks, with the seed post focusing on ConvNets in ImageNet and this post on an early application of backpropagation to handwritten zip code recognition._
- [x] `649acfbf-16a7-47ef-8a33-51f49f01b7e1` — **nntutorial**
  - _reason: Both posts are directly related to neural networks and deep learning, with the seed post discussing ConvNets in the ImageNet challenge and this post being a 'Hacker's guide to Neural Networks' tutorial._

**Rejected by Gemini — tick [x] to ADD (override)**:

- [ ] `e6b06557-6d65-4ee6-9790-07e60f065019` — **2026-02-12-microgpt**
  - _rejected because: The seed post is about Convolutional Neural Networks and ImageNet, while this post is about GPTs and language models, which are distinct topics despite both being deep learning._
- [ ] `b87baa3b-38fd-466f-858d-4e765e89464d` — **2015-11-20-ai**
  - _rejected because: The seed post discusses a specific computer vision challenge and ConvNets, while this post is a fictional story about AI in a broader, more speculative sense._
- [ ] `1309f035-93d7-403b-a890-0540bd2eaec8` — **2018-01-20-medium**
  - _rejected because: The seed post is about a computer vision challenge, while this post is about the author's blogging platform choices and activity, which is not thematically related._
- [ ] `58f62ce2-923d-436d-bca2-c6a5c3e18ef3` — **2015-05-21-rnn-effectiveness**
  - _rejected because: The seed post focuses on Convolutional Neural Networks for image recognition, while this post discusses Recurrent Neural Networks (RNNs) for image captioning, which are different network architectures and applications._
- [ ] `17808433-ad82-4ea2-9fb3-98ec88aafb7e` — **2014-07-02-visualizing-top-tweeps-with-t-sne-in-Javascript**
  - _rejected because: The seed post is about a computer vision challenge using ConvNets, while this post is about visualizing high-dimensional data using t-SNE, a different machine learning technique and application._
- [ ] `97728ae4-a085-4bda-9176-c088e1431b73` — **2013-11-27-quantifying-hacker-news**
  - _rejected because: The seed post is about a computer vision challenge, while this post is about analyzing data from Hacker News, which is a different domain and type of analysis._
- [ ] `919a9465-5f46-4119-88a5-ab7c783e0fa9` — **2013-11-23-chrome-extension-programming**
  - _rejected because: The seed post is about a computer vision challenge, while this post is about programming Chrome extensions, which is unrelated._
- [ ] `d7ad6c9c-f109-4556-a211-44f8b3e0a3e5` — **2020-06-11-biohacking-lite**
  - _rejected because: The seed post is about a computer vision challenge, while this post is about personal health, exercise, and diet, which is not thematically related._
- [ ] `2e701e80-befb-4258-a53a-fb204df46181` — **2021-03-27-forward-pass**
  - _rejected because: The seed post is about Convolutional Neural Networks and ImageNet, while this post is a short story inspired by GPT-3 and Turing tests, focusing on language models rather than computer vision._
- [ ] `59724873-f8c4-4822-80ee-983205b30475` — **2019-04-25-recipe**
  - _rejected because: The seed post discusses a specific computer vision challenge, while this post is about common mistakes in training neural networks in a general sense, without a specific thematic link to ImageNet or ConvNets beyond the broad field of neural networks._

---

## Seed 15/20: 2014-08-03-quantifying-productivity
_id: `7010382f-4855-41b6-915f-bccebb511234` · mentions in graph: 9_

> I'm always on a lookout for interesting datasets to collect, analyze and interpret. And what better dataset to collect/analyze than the *meta-dataset* of my own activity collecting/analyzing other datasets? How much time do I **really* spend working per day? How do I spend most of that time? What ma...

**Gemini proposes these as RELATED** — tick [x] to KEEP, clear [ ] to DROP:

- [x] `97728ae4-a085-4bda-9176-c088e1431b73` — **2013-11-27-quantifying-hacker-news**
  - _reason: Both posts discuss the author's personal interest in collecting, analyzing, and interpreting datasets related to their own activity or interests, specifically 'quantifying productivity' and 'quantifying Hacker News'._
- [x] `d7ad6c9c-f109-4556-a211-44f8b3e0a3e5` — **2020-06-11-biohacking-lite**
  - _reason: Both posts discuss the author's personal efforts to collect and analyze data about their own activities and habits, with the seed focusing on productivity and this post on health and biohacking._

**Rejected by Gemini — tick [x] to ADD (override)**:

- [ ] `e6b06557-6d65-4ee6-9790-07e60f065019` — **2026-02-12-microgpt**
  - _rejected because: This post is about building a GPT model, which is a specific technical project unrelated to quantifying personal productivity._
- [ ] `5fb0613e-263a-486b-b400-4febd8b2264b` — **(unknown id)**
  - _rejected because: This post discusses a historical paper on backpropagation and neural networks, which is a technical topic unrelated to personal productivity data analysis._
- [ ] `b87baa3b-38fd-466f-858d-4e765e89464d` — **2015-11-20-ai**
  - _rejected because: This post is a short story about AI, which is a creative writing piece and a broad topic, not directly related to quantifying personal productivity._
- [ ] `1309f035-93d7-403b-a890-0540bd2eaec8` — **2018-01-20-medium**
  - _rejected because: This post discusses the author's blogging platform choices and activity, which is a meta-discussion about blogging, not about quantifying productivity through data analysis._
- [ ] `1936f8b5-9601-4767-ac52-f5e2b728af04` — **2015-10-25-selfie**
  - _rejected because: This post is about using Convolutional Neural Networks for image recognition and amusement, a specific technical application unrelated to personal productivity data._
- [ ] `ffb6007e-7be2-4653-b4db-b0a55dfbef92` — **2015-03-30-breaking-convnets**
  - _rejected because: This post discusses the limitations and caveats of Convolutional Networks, a technical topic in machine learning, not related to personal productivity data analysis._
- [ ] `979ee142-a973-42f0-95d5-26f38c03a407` — **2014-07-03-feature-learning-escapades**
  - _rejected because: This post is about a specific research project on large-scale video classification using CNNs, which is a technical machine learning topic unrelated to personal productivity._
- [ ] `17808433-ad82-4ea2-9fb3-98ec88aafb7e` — **2014-07-02-visualizing-top-tweeps-with-t-sne-in-Javascript**
  - _rejected because: This post discusses visualizing high-dimensional data using t-SNE, a specific data visualization technique, not directly related to the theme of quantifying personal productivity._
- [ ] `919a9465-5f46-4119-88a5-ab7c783e0fa9` — **2013-11-23-chrome-extension-programming**
  - _rejected because: This post is about programming Chrome extensions, a technical skill unrelated to collecting and analyzing personal productivity data._
- [ ] `2e701e80-befb-4258-a53a-fb204df46181` — **2021-03-27-forward-pass**
  - _rejected because: This post is a short story inspired by GPT-3 and Turing tests, which is a creative writing piece on AI, not related to quantifying personal productivity._

---

## Seed 16/20: 2012-10-22-state-of-computer-vision
_id: `d14e0f1f-a3e2-450c-a23f-8b24a7689f8f` · mentions in graph: 9_

> <img src="/assets/obamafunny.jpg" width="100%" /> The picture above is funny.  But for me it is also one of those examples that make me sad about the outlook for AI and for Computer Vision. What would it take for a computer to understand this image as you or I do? I challenge you to think explicitly...

**Gemini proposes these as RELATED** — tick [x] to KEEP, clear [ ] to DROP:

- [x] `1936f8b5-9601-4767-ac52-f5e2b728af04` — **2015-10-25-selfie**
  - _reason: Both posts discuss the capabilities and limitations of computer vision, with the seed post questioning what it takes for a computer to understand an image and this post discussing how Convolutional Neural Networks are used for visual recognition._
- [x] `ffb6007e-7be2-4653-b4db-b0a55dfbef92` — **2015-03-30-breaking-convnets**
  - _reason: Both posts discuss the capabilities and limitations of computer vision and AI, with the seed post lamenting the state of AI/Computer Vision and this post discussing the 'human-level performance' claims of Convolutional Networks in visual recognition._
- [x] `979ee142-a973-42f0-95d5-26f38c03a407` — **2014-07-03-feature-learning-escapades**
  - _reason: Both posts discuss the application of Convolutional Neural Networks (ConvNets) to visual tasks, with the seed post questioning computer understanding of images and this post detailing large-scale video classification with ConvNets._
- [x] `2599441e-34b5-406e-bcd3-e060026b98e5` — **2014-09-02-what-i-learned-from-competing-against-a-convnet-on-imagenet**
  - _reason: Both posts are directly related to computer vision and the challenges of image understanding, with the seed post questioning what it takes for a computer to understand an image and this post discussing the ImageNet Large Scale Visual Recognition Challenge._
- [x] `096ea70a-1459-47a9-b0e0-6cd4870d74f8` — **2011-04-27-manually-classifying-cifar10**
  - _reason: Both posts discuss computer vision tasks, specifically image classification, with the seed post questioning computer understanding of images and this post detailing the CIFAR-10 image classification dataset and its state of the art._
- [x] `649acfbf-16a7-47ef-8a33-51f49f01b7e1` — **nntutorial**
  - _reason: Both posts discuss the broader field of AI and neural networks, with the seed post questioning the outlook for AI and Computer Vision, and this post serving as a tutorial on neural networks, a core component of modern AI and computer vision._

**Rejected by Gemini — tick [x] to ADD (override)**:

- [ ] `e6b06557-6d65-4ee6-9790-07e60f065019` — **2026-02-12-microgpt**
  - _rejected because: This post focuses on training and inferencing a GPT model, which is a language model, while the seed post is specifically about computer vision and image understanding._
- [ ] `5fb0613e-263a-48b6-b400-4febd8b2264b` — **2022-03-14-lecun1989**
  - _rejected because: This post discusses the historical significance of backpropagation in neural networks for handwritten zip code recognition, which is a specific application of neural networks, but the seed post is a broader reflection on the state of computer vision and AI's ability to understand images._
- [ ] `b87baa3b-38fd-466f-858d-4e765e89464d` — **2015-11-20-ai**
  - _rejected because: This post is a fictional story about AI and its future, which is a different thematic focus than the seed post's technical discussion on the current state and challenges of computer vision._
- [ ] `1309f035-93d7-403b-a890-0540bd2eaec8` — **2018-01-20-medium**
  - _rejected because: This post is about the author's blogging platform choices and activity, which is not thematically related to computer vision or AI._
- [ ] `17808433-ad82-4ea2-9fb3-98ec88aafb7e` — **2014-07-02-visualizing-top-tweeps-with-t-sne-in-Javascript**
  - _rejected because: This post discusses visualizing high-dimensional data using t-SNE, which is a data visualization technique, not directly related to the core theme of computer vision's ability to understand images._
- [ ] `97728ae4-a085-4bda-9176-c088e1431b73` — **2013-11-27-quantifying-hacker-news**
  - _rejected because: This post is about analyzing Hacker News activity, which is a data analysis topic unrelated to computer vision or AI understanding of images._
- [ ] `919a9465-5f46-4119-88a5-ab7c783e0fa9` — **2013-11-23-chrome-extension-programming**
  - _rejected because: This post is about programming Chrome extensions, which is a software development topic unrelated to computer vision or AI._
- [ ] `d7ad6c9c-f109-4556-a211-44f8b3e0a3e5` — **2020-06-11-biohacking-lite**
  - _rejected because: This post is about biohacking and personal health, which is not thematically related to computer vision or AI._
- [ ] `2e701e80-befb-4258-a53a-fb204df46181` — **2021-03-27-forward-pass**
  - _rejected because: This post is a short story inspired by GPT-3 and the Turing Test, focusing on language models and AI consciousness, which is distinct from the seed post's focus on computer vision and image understanding._
- [ ] `59724873-f8c4-4822-80ee-983205b30475` — **2019-04-25-recipe**
  - _rejected because: This post discusses common mistakes in training neural networks, which is a practical guide for machine learning practitioners, but not directly about the fundamental challenges of computer vision as discussed in the seed post._

---

## Seed 17/20: 2011-04-27-manually-classifying-cifar10
_id: `096ea70a-1459-47a9-b0e0-6cd4870d74f8` · mentions in graph: 9_

> ### CIFAR-10  > Note, this post is from 2011 and slightly outdated in some places.  <div style="text-align:center;"><img src="/assets/cifar_preview.png"></div>  **Statistics**. CIFAR-10 consists of 50,000 training images, all of them in 1 of 10 categories (displayed left). The test set consists of 1...

**Gemini proposes these as RELATED** — tick [x] to KEEP, clear [ ] to DROP:

- [x] `5fb0613e-263a-48b6-b400-4febd8b2264b` — **2022-03-14-lecun1989**
  - _reason: Both posts discuss historical or foundational aspects of neural networks and their applications in image classification, with the seed post mentioning CIFAR-10 and the candidate discussing handwritten zip code recognition._
- [x] `ffb6007e-7be2-4653-b4db-b0a55dfbef92` — **2015-03-30-breaking-convnets**
  - _reason: Both posts discuss Convolutional Networks and their performance in visual recognition problems, with the seed post focusing on CIFAR-10 classification accuracy and the candidate discussing general performance and caveats._
- [x] `979ee142-a973-42f0-95d5-26f38c03a407` — **2014-07-03-feature-learning-escapades**
  - _reason: Both posts discuss Convolutional Neural Networks (ConvNets) and their application in classification tasks, with the seed post focusing on CIFAR-10 and the candidate on large-scale video classification._
- [x] `2599441e-34b5-406e-bcd3-e060026b98e5` — **2014-09-02-what-i-learned-from-competing-against-a-convnet-on-imagenet**
  - _reason: Both posts discuss image classification challenges and the performance of Convolutional Neural Networks, with the seed post mentioning CIFAR-10 and the candidate focusing on the ImageNet Large Scale Visual Recognition Challenge._
- [x] `d14e0f1f-a3e2-450c-a23f-8b24a7689f8f` — **2012-10-22-state-of-computer-vision**
  - _reason: Both posts discuss the challenges and state of Computer Vision and AI, with the seed post focusing on image classification accuracy and the candidate on the broader understanding of images by computers._
- [x] `649acfbf-16a7-47ef-8a33-51f49f01b7e1` — **nntutorial**
  - _reason: Both posts are directly related to neural networks and deep learning, with the seed post discussing CIFAR-10 classification and the candidate being a 'Hacker's guide to Neural Networks' tutorial._

**Rejected by Gemini — tick [x] to ADD (override)**:

- [ ] `e6b06557-6d65-4ee6-9790-07e60f065019` — **2026-02-12-microgpt**
  - _rejected because: The candidate post discusses training and inferencing a GPT model, which is a language model, while the seed post is specifically about image classification with CIFAR-10._
- [ ] `b87baa3b-38fd-466f-858d-4e765e89464d` — **2015-11-20-ai**
  - _rejected because: The candidate post is a short story about AI and supervised learning in a general sense, lacking the specific technical focus on image classification or datasets like CIFAR-10 found in the seed._
- [ ] `1309f035-93d7-403b-a890-0540bd2eaec8` — **2018-01-20-medium**
  - _rejected because: The candidate post is about the author's blogging platform choices and activity, which is not thematically related to image classification or the CIFAR-10 dataset._
- [ ] `1936f8b5-9601-4767-ac52-f5e2b728af04` — **2015-10-25-selfie**
  - _rejected because: While both mention Convolutional Neural Networks and visual recognition, the candidate post focuses on a 'fun experiment' with selfies and warping models for amusement, which is a different thematic focus than the benchmark classification task in the seed._
- [ ] `17808433-ad82-4ea2-9fb3-98ec88aafb7e` — **2014-07-02-visualizing-top-tweeps-with-t-sne-in-Javascript**
  - _rejected because: The candidate post discusses visualizing high-dimensional data using t-SNE, which is a general data visualization technique, not specifically tied to image classification or the CIFAR-10 dataset._
- [ ] `97728ae4-a085-4bda-9176-c088e1431b73` — **2013-11-27-quantifying-hacker-news**
  - _rejected because: The candidate post is about analyzing and quantifying activity on Hacker News, which is unrelated to image classification or the CIFAR-10 dataset._
- [ ] `919a9465-5f46-4119-88a5-ab7c783e0fa9` — **2013-11-23-chrome-extension-programming**
  - _rejected because: The candidate post is about programming Chrome extensions, which is a software development topic unrelated to image classification or the CIFAR-10 dataset._
- [ ] `d7ad6c9c-f109-4556-a211-44f8b3e0a3e5` — **2020-06-11-biohacking-lite**
  - _rejected because: The candidate post discusses personal health, exercise, and diet ('biohacking'), which is not related to image classification or the CIFAR-10 dataset._
- [ ] `2e701e80-befb-4258-a53a-fb204df46181` — **2021-03-27-forward-pass**
  - _rejected because: The candidate post is a short story inspired by GPT-3 and Turing Tests, focusing on language models and AI consciousness, which is distinct from image classification with CIFAR-10._
- [ ] `59724873-f8c4-4822-80ee-983205b30475` — **2019-04-25-recipe**
  - _rejected because: While both mention neural networks, the candidate post focuses on common mistakes and practical advice for training neural nets, rather than a specific dataset or classification task like CIFAR-10._

---

## Seed 18/20: 2015-05-21-rnn-effectiveness
_id: `58f62ce2-923d-436d-bca2-c6a5c3e18ef3` · mentions in graph: 8_

> There's something magical about Recurrent Neural Networks (RNNs). I still remember when I trained my first recurrent network for [Image Captioning](http://cs.stanford.edu/people/karpathy/deepimagesent/). Within a few dozen minutes of training my first baby model (with rather arbitrarily-chosen hyper...

**Gemini proposes these as RELATED** — tick [x] to KEEP, clear [ ] to DROP:

- [x] `e6b06557-6d65-4ee6-9790-07e60f065019` — **2026-02-12-microgpt**
  - _reason: Both posts discuss specific types of neural networks (RNNs and GPTs) and their effectiveness in generating content or descriptions._
- [x] `649acfbf-16a7-47ef-8a33-51f49f01b7e1` — **nntutorial**
  - _reason: Both posts are about neural networks, with the candidate post being a tutorial on neural networks, a foundational topic for RNNs discussed in the seed._
- [x] `2e701e80-befb-4258-a53a-fb204df46181` — **2021-03-27-forward-pass**
  - _reason: Both posts discuss the capabilities and implications of advanced neural networks, specifically mentioning GPT-3 in the candidate post, which is a successor to the themes of generative models in the seed._

**Rejected by Gemini — tick [x] to ADD (override)**:

- [ ] `5fb0613e-263a-48b6-b400-4febd8b2264b` — **2022-03-14-lecun1989**
  - _rejected because: The candidate post discusses the historical significance of backpropagation in neural networks, which is a general technique, not specifically tied to RNNs or their effectiveness as in the seed._
- [ ] `b87baa3b-38fd-466f-858d-4e765e89464d` — **2015-11-20-ai**
  - _rejected because: The candidate post is a fictional story about AI, which is too broad to be thematically related to the specific technical discussion of RNN effectiveness in the seed._
- [ ] `1309f035-93d7-403b-a890-0540bd2eaec8` — **2018-01-20-medium**
  - _rejected because: The candidate post is about the author's blogging platform choices and activity, which is not thematically related to recurrent neural networks._
- [ ] `1936f8b5-9601-4767-ac52-f5e2b728af04` — **2015-10-25-selfie**
  - _rejected because: The candidate post discusses Convolutional Neural Networks for visual recognition and their fun applications, which is a different type of neural network and application than RNNs for image captioning._
- [ ] `ffb6007e-7be2-4653-b4db-b0a55dfbef92` — **2015-03-30-breaking-convnets**
  - _rejected because: The candidate post discusses the limitations and caveats of Convolutional Networks in visual recognition, which is a different type of neural network and focus than the seed's discussion of RNN effectiveness._
- [ ] `979ee142-a973-42f0-95d5-26f38c03a407` — **2014-07-03-feature-learning-escapades**
  - _rejected because: The candidate post discusses large-scale video classification with Convolutional Neural Networks, which is a different specific technique and application than RNNs for image captioning._
- [ ] `17808433-ad82-4ea2-9fb3-98ec88aafb7e` — **2014-07-02-visualizing-top-tweeps-with-t-sne-in-Javascript**
  - _rejected because: The candidate post discusses visualizing high-dimensional data using t-SNE, which is a data visualization technique, not directly related to the effectiveness of recurrent neural networks._
- [ ] `97728ae4-a085-4bda-9176-c088e1431b73` — **2013-11-27-quantifying-hacker-news**
  - _rejected because: The candidate post is about analyzing Hacker News activity, which is a data analysis topic unrelated to recurrent neural networks._
- [ ] `919a9465-5f46-4119-88a5-ab7c783e0fa9` — **2013-11-23-chrome-extension-programming**
  - _rejected because: The candidate post is about programming Chrome extensions, which is a software development topic unrelated to recurrent neural networks._
- [ ] `d7ad6c9c-f109-4556-a211-44f8b3e0a3e5` — **2020-06-11-biohacking-lite**
  - _rejected because: The candidate post is about biohacking and personal health, which is not thematically related to recurrent neural networks._

---

## Seed 19/20: 2014-07-01-switching-to-jekyll
_id: `8727b22c-7beb-41c3-b796-8bd15bdce3e5` · mentions in graph: 8_

> Inspired by [Mark Reid's](https://twitter.com/mdreid) blog post [Switching from Jekyll to Hakyll](http://mark.reid.name/blog/switching-to-hakyll.html) I decided to abandon Wordpress and give Jekyll a try (note, I currently do not yet feel pro enough to switch to Haskell-based Hakyll). I can confiden...

**Gemini proposes these as RELATED** — tick [x] to KEEP, clear [ ] to DROP:

- [x] `1309f035-93d7-403b-a890-0540bd2eaec8` — **2018-01-20-medium**
  - _reason: The candidate post discusses the author's shift to using Medium for blogging, which is thematically related to the seed post's discussion of switching from Wordpress to Jekyll for blogging._

**Rejected by Gemini — tick [x] to ADD (override)**:

- [ ] `e6b06557-6d65-4ee6-9790-07e60f065019` — **2026-02-12-microgpt**
  - _rejected because: The candidate post is about a new art project involving a GPT model, which is a different topic from blog platform migration._
- [ ] `5fb0613e-263a-48b6-b400-4febd8b2264b` — **2022-03-14-lecun1989**
  - _rejected because: The candidate post discusses a historical paper on backpropagation in neural networks, which is unrelated to blog platform choices._
- [ ] `b87baa3b-38fd-466f-858d-4e765e89464d` — **2015-11-20-ai**
  - _rejected because: The candidate post is a short story about AI, which is not related to blog platform migration._
- [ ] `1936f8b5-9601-4767-ac52-f5e2b728af04` — **2015-10-25-selfie**
  - _rejected because: The candidate post discusses using Convolutional Neural Networks for image recognition and amusement, which is unrelated to blog platform choices._
- [ ] `ffb6007e-7be2-4653-b4db-b0a55dfbef92` — **2015-03-30-breaking-convnets**
  - _rejected because: The candidate post discusses the effectiveness and caveats of Convolutional Networks, a topic unrelated to blog platform migration._
- [ ] `979ee142-a973-42f0-95d5-26f38c03a407` — **2014-07-03-feature-learning-escapades**
  - _rejected because: The candidate post describes an internship project on large-scale video classification with CNNs, which is unrelated to blog platform choices._
- [ ] `17808433-ad82-4ea2-9fb3-98ec88aafb7e` — **2014-07-02-visualizing-top-tweeps-with-t-sne-in-Javascript**
  - _rejected because: The candidate post discusses visualizing high-dimensional data using t-SNE, a topic unrelated to blog platform migration._
- [ ] `97728ae4-a085-4bda-9176-c088e1431b73` — **2013-11-27-quantifying-hacker-news**
  - _rejected because: The candidate post is about analyzing Hacker News activity, which is unrelated to blog platform migration._
- [ ] `919a9465-5f46-4119-88a5-ab7c783e0fa9` — **2013-11-23-chrome-extension-programming**
  - _rejected because: The candidate post discusses programming Chrome extensions, which is unrelated to blog platform choices._
- [ ] `d7ad6c9c-f109-4556-a211-44f8b3e0a3e5` — **2020-06-11-biohacking-lite**
  - _rejected because: The candidate post is about biohacking and health, which is unrelated to blog platform migration._

---

## Seed 20/20: 2014-04-26-datascience-weekly-interview
_id: `2fc7e67e-8e1a-4367-9606-9137d48d6af8` · mentions in graph: 7_

> I thought I should link this: I've given an interview ~two months ago about ConvNetJS, some of my background and a few perspectives on neural net trends and where the field seems to be going, at least in academia. Find it here:  [http://www.datascienceweekly.org/blog/14-training-deep-learning-models...

**Gemini proposes these as RELATED** — tick [x] to KEEP, clear [ ] to DROP:

- [x] `e6b06557-6d65-4ee6-9790-07e60f065019` — **2026-02-12-microgpt**
  - _reason: Both posts discuss neural networks, with the seed post mentioning 'neural net trends' and the candidate post detailing a 'GPT' (Generative Pre-trained Transformer), which is a type of neural network._
- [x] `5fb0613e-263a-48b6-b400-4febd8b2264b` — **2022-03-14-lecun1989**
  - _reason: Both posts discuss neural networks, with the seed post mentioning 'neural net trends' and the candidate post discussing a historically significant paper on 'Backpropagation Applied to Handwritten Zip Code Recognition' using a neural net._
- [x] `b87baa3b-38fd-466f-858d-4e765e89464d` — **2015-11-20-ai**
  - _reason: Both posts discuss AI and neural networks, with the seed post mentioning 'neural net trends' and the candidate post extrapolating current technology in AI, specifically mentioning 'scaling up supervised learning'._
- [x] `1936f8b5-9601-4767-ac52-f5e2b728af04` — **2015-10-25-selfie**
  - _reason: Both posts discuss neural networks, with the seed post mentioning 'neural net trends' and the candidate post focusing on 'Convolutional Neural Networks' and their applications._
- [x] `ffb6007e-7be2-4653-b4db-b0a55dfbef92` — **2015-03-30-breaking-convnets**
  - _reason: Both posts discuss neural networks, with the seed post mentioning 'neural net trends' and the candidate post focusing on 'Convolutional Networks' and their performance._
- [x] `979ee142-a973-42f0-95d5-26f38c03a407` — **2014-07-03-feature-learning-escapades**
  - _reason: Both posts discuss neural networks, with the seed post mentioning 'neural net trends' and the candidate post detailing 'Large-scale Video Classification with Convolutional Neural Networks'._
- [x] `2e701e80-befb-4258-a53a-fb204df46181` — **2021-03-27-forward-pass**
  - _reason: Both posts discuss neural networks, with the seed post mentioning 'neural net trends' and the candidate post referencing 'GPT-3', a prominent neural network model._
- [x] `59724873-f8c4-4822-80ee-983205b30475` — **2019-04-25-recipe**
  - _reason: Both posts discuss neural networks, with the seed post mentioning 'neural net trends' and the candidate post discussing 'neural net mistakes' and 'how a convonet works'._
- [x] `2599441e-34b5-406e-bcd3-e060026b98e5` — **2014-09-02-what-i-learned-from-competing-against-a-convnet-on-imagenet**
  - _reason: Both posts discuss neural networks, with the seed post mentioning 'neural net trends' and the candidate post discussing competing against a 'ConvNet on ImageNet'._
- [x] `d14e0f1f-a3e2-450c-a23f-8b24a7689f8f` — **2012-10-22-state-of-computer-vision**
  - _reason: Both posts discuss AI and neural networks, with the seed post mentioning 'neural net trends' and the candidate post reflecting on the 'outlook for AI and for Computer Vision' and what it would take for a computer to understand an image._
- [x] `096ea70a-1459-47a9-b0e0-6cd4870d74f8` — **2011-04-27-manually-classifying-cifar10**
  - _reason: Both posts discuss neural networks, with the seed post mentioning 'neural net trends' and the candidate post discussing 'CIFAR-10' and classification accuracy, which is a common benchmark for neural networks._
- [x] `58f62ce2-923d-436d-bca2-c6a5c3e18ef3` — **2015-05-21-rnn-effectiveness**
  - _reason: Both posts discuss neural networks, with the seed post mentioning 'neural net trends' and the candidate post focusing on 'Recurrent Neural Networks (RNNs)' and their applications like 'Image Captioning'._
- [x] `649acfbf-16a7-47ef-8a33-51f49f01b7e1` — **nntutorial**
  - _reason: Both posts discuss neural networks, with the seed post mentioning 'neural net trends' and the candidate post being a 'Hacker's guide to Neural Networks'._
- [x] `71d45412-30c7-416b-aa36-faf3f03ea868` — **2016-05-31-rl**
  - _reason: Both posts discuss neural networks, with the seed post mentioning 'neural net trends' and the candidate post focusing on 'Reinforcement Learning (RL)', which often involves neural networks._

**Rejected by Gemini — tick [x] to ADD (override)**:

- [ ] `1309f035-93d7-403b-a890-0540bd2eaec8` — **2018-01-20-medium**
  - _rejected because: The candidate post discusses blogging platforms and personal posting habits, which is not thematically related to neural networks or data science trends._
- [ ] `17808433-ad82-4ea2-9fb3-98ec88aafb7e` — **2014-07-02-visualizing-top-tweeps-with-t-sne-in-Javascript**
  - _rejected because: The candidate post discusses visualizing high-dimensional data using t-SNE, which is a data science technique but not specifically linked to neural network trends as highlighted in the seed post._
- [ ] `97728ae4-a085-4bda-9176-c088e1431b73` — **2013-11-27-quantifying-hacker-news**
  - _rejected because: The candidate post discusses analyzing Hacker News activity, which is a data analysis topic but not specifically related to neural networks or deep learning trends._
- [ ] `919a9465-5f46-4119-88a5-ab7c783e0fa9` — **2013-11-23-chrome-extension-programming**
  - _rejected because: The candidate post discusses programming Chrome extensions, which is a software development topic and not thematically related to neural networks or data science trends._
- [ ] `d7ad6c9c-f109-4556-a211-44f8b3e0a3e5` — **2020-06-11-biohacking-lite**
  - _rejected because: The candidate post discusses personal health, exercise, and diet, which is not thematically related to neural networks or data science trends._
- [ ] `7010382f-4855-41b6-915f-bccebb511234` — **2014-08-03-quantifying-productivity**
  - _rejected because: The candidate post discusses quantifying personal productivity, which is a self-improvement and data analysis topic but not specifically related to neural networks or deep learning trends._
- [ ] `8727b22c-7beb-41c3-b796-8bd15bdce3e5` — **2014-07-01-switching-to-jekyll**
  - _rejected because: The candidate post discusses switching blogging platforms from Wordpress to Jekyll, which is a technical blog management topic and not thematically related to neural networks or data science trends._
- [ ] `78d4e228-302e-469d-b654-0be5190ec4cd` — **2021-06-21-blockchain**
  - _rejected because: The candidate post discusses blockchain technology, which is a distinct technical field and not thematically related to neural networks or deep learning trends._
- [ ] `dd671e69-b246-4f22-8ec8-4b369b1a1102` — **2016-09-07-phd**
  - _rejected because: The candidate post offers advice on pursuing a PhD, which is an academic and career guidance topic and not thematically related to neural networks or data science trends._

---
