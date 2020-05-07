import tensorflow as tf
import matplotlib.pyplot as plt
import numpy as np
from tensorflow.keras.applications import vgg19, VGG19

class Model(object):
    def __init__(self):
        self.learning_rate = 2
        self.alpha = 1e-3
        self.beta = 1
        # Layers in which we compute the style loss
        self.style_layers = ['block1_conv1', 'block2_conv1', 'block3_conv1', 'block4_conv1', 'block5_conv1']
        # Layer in which we compute the content loss
        self.content_layer = 'block4_conv2'
    
    def load(self):
        self.model = VGG19(include_top=False, weights='imagenet')
        print("VGG19 model successfully loaded.")
        self.layer_outputs = dict([(layer.name, layer.output) for layer in model.layers])
    
    def gen_input(self):
        with tf.compat.v1.variable_scope("gen_input"):
            self.input = tf.compat.v1.get_variable("in_img", shape=([1, self.img_height, self.img_width, 3]), dtype=tf.float32, initializer=tf.zeros_initializer())

    # This section contains the loss function and four helper functions.
    def _content_loss(self, img, content):
        return tf.math.reduce_sum(tf.math.square(img - content))

    def _gram_matrix(self, img, area, num_channels):
        """
        Compute the gram matrix G for an image tensor

        :param img: the feature map of an image, of shape (h, w, num_channels)
        :param area: h * w for some image
        :param num_channels: the number of channels in some image feature map
        """
        mat = tf.reshape(img, (area, num_channels))
        gram = tf.matmul(tf.transpose(mat), mat)
        return gram

    def _layer_style_loss(self, img, style):
        """
        Compute the style loss in a single layer

        :param img: the input image
        :param style: the style image
        """
        h, w, num_channels = img.shape
        area = h * w

        gram_style = _gram_matrix(style, area, num_channels)
        gram_img = _gram_matrix(img, area, num_channels)

        loss = tf.math.reduce_sum(tf.math.square(gram_img - gram_style)) / (area * num_channels * 2)**2
        return loss

    def _style_loss(self, map_set):
        """
        Compute the total style loss across all layers

        :param map_set: a set of all feature maps for the style image
        """
        num_layers = map_set.shape[0]

        # Initialize the weights for all style layers; this hyperparameter can be tuned
        # General idea: deeper layers are more important
        layer_weights = [0.5 * i + 0.5 for i in range(num_layers)]

        layer_losses = []
        for i in range(num_layers):
            layer_loss = _layer_style_loss(map_set[i], self.layer_outputs[self.style_layers[i]]) * layer_weights[i]

        return sum(layer_losses)

    def loss(self, img):
        """
        Compute the total loss of the model
        """
        with tf.compat.v1.variable_scope("loss"):
            # Content loss
            with tf.compat.v1.Session() as sess:
                sess.run(self.input.assign(self.content))
                combination_out = self.layer_outputs[self.content_layer]
                content_out = sess.run(combination_out)
            l_content = self._content_loss(content_out, combination_out)

            # Style loss
            with tf.compat.v1.Session() as sess:
                sess.run(self.input_img.assign(self.style))
                style_maps = sess.run(self.layer_outputs[layer] for layer in self.style_layers])                              
            l_style = self._style_loss(style_maps)

            # Total loss
            self.loss = self.alpha * l_content + self.beta * l_style


    # This section contains image processing
    def preprocess(self, filepath):
        img = plt.imread(filepath)
        img = vgg19.preprocess_input(img)
        return img

    def deprocess(self, img):
        mean_red = 123.68
        mean_green = 116.779
        mean_blue = 103.939
        img = img[:, :, ::-1]
        
        pass

    # This section trains the model using stochastic gradient descent
    def train(self):
        self.optimizer = tf.compat.v1.train.GradientDescentOptimizer(self.learning_rate)
        pass
    