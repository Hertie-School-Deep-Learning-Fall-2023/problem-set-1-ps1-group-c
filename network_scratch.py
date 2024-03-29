import time
import numpy as np
import utils


class NeuralNetwork():
    def __init__(self, layer_shapes, epochs=50, learning_rate=0.01, random_state=1):

        #Define learning paradigms
        self.epochs = epochs
        self.learning_rate = learning_rate
        self.random_state = random_state

        #Define network architecture: no. of layers and neurons
        #layer_shapes[i] is the shape of the input that gets multiplied 
        #to the weights for the layer (e.g. layer_shapes[0] is 
        #the number of input features)

        self.layer_shapes = layer_shapes
        self.weights = self._initialize_weights()

        #Initialize weight vectors calling the function
        #Initialize list of layer inputs before and after  
        #activation as lists of zeros.
        
        # self.A stores the inputs to each layer after activation is applied
        self.A = [None] * len(layer_shapes)
        # self.Z stores the inputs to each layer before activation is applied
        self.Z = [None] * (len(layer_shapes)-1)

        # define activation functions for the different layers
        self.activation_func = utils.sigmoid
        self.activation_func_deriv = utils.sigmoid_deriv
        self.output_func = utils.softmax
        self.output_func_deriv = utils.softmax_deriv
        self.cost_func = utils.mse
        self.cost_func_deriv = utils.mse_deriv

        # construct a weight matrix # rows = no. neurons in layer i, # cols = no. neurons in layer i-1
        # dimensions enable dot product between layers
    def _initialize_weights(self):

        np.random.seed(self.random_state)
        self.weights = [] 

        for i in range(1, len(self.layer_shapes)):
            weight = np.random.rand(self.layer_shapes[i], self.layer_shapes[i-1]) - 0.5
            self.weights.append(weight)

        return self.weights


    def _forward_pass(self, x_train):
        '''
        TODO: Implement the forward propagation algorithm.
        The method should return the output of the network.
        '''
        # first layer is the input layer
        self.A[0] = x_train
        for i in range(len(self.weights)):
            self.Z[i] = np.dot(self.weights[i], self.A[i])
            # apply input activation function (sigmoid) to all layers except the last one, on which we apply the output activation function (softmax)
            if i < len(self.weights) - 1:
                self.A[i + 1] = self.activation_func(self.Z[i])
            else:
                self.A[i + 1] = self.output_func(self.Z[i])
        # return the output of the network, which is the last layer (A[-1])
        return self.A[-1]


    def _backward_pass(self, y_train, output):
        '''
        TODO: Implement the backpropagation algorithm responsible for updating the weights of the neural network.
        The method should return a list of the weight gradients which are used to update the weights in self._update_weights().
        '''
        weight_gradients = [None] * len(self.weights)
        # compute the first delta term outside of the loop
        # error at the output layer: derivative of the cost function * the derivative of the output activation function w.r.t to the input of the output layer
        delta = self.cost_func_deriv(y_train, output) * self.output_func_deriv(self.Z[-1])
        
        # start at last hidden layer (len-1) and go backwards to the input layer (-1)
        for i in range(len(self.weights) - 1, -1, -1):
            weight_gradients[i] = np.outer(delta, self.A[i])
            if i > 0: # don't compute delta for the input layer (i=0)
                delta = np.dot(self.weights[i].T, delta) * self.activation_func_deriv(self.Z[i - 1])
                
        return weight_gradients


    def _update_weights(self,weight_gradients):
        '''
        TODO: Update the network weights according to stochastic gradient descent.
        '''
        for i in range(len(self.weights)):
            self.weights[i] -= self.learning_rate * weight_gradients[i]


    def _print_learning_progress(self, start_time, iteration, x_train, y_train, x_val, y_val):
        train_accuracy = self.compute_accuracy(x_train, y_train)
        val_accuracy = self.compute_accuracy(x_val, y_val)
        print(
            f'Epoch: {iteration + 1}, ' \
            f'Training Time: {time.time() - start_time:.2f}s, ' \
            f'Training Accuracy: {train_accuracy * 100:.2f}%, ' \
            f'Validation Accuracy: {val_accuracy * 100:.2f}%'
            )

        return train_accuracy, val_accuracy
    

    def compute_accuracy(self, x_val, y_val):
        predictions = []

        for x, y in zip(x_val, y_val):
            pred = self.predict(x)
            predictions.append(pred == np.argmax(y))

        return np.mean(predictions)


    def predict(self, x):
        '''
        TODO: Implement the prediction making of the network.
        The method should return the index of the most likeliest output class.
        '''
        # run through forward pass and return index of the most likely output class
        return np.argmax(self._forward_pass(x))


    def fit(self, x_train, y_train, x_val, y_val):

        history = {'accuracy': [], 'val_accuracy': []}
        start_time = time.time()

        for iteration in range(self.epochs):
            for x, y in zip(x_train, y_train):
                output = self._forward_pass(x)
                weight_gradients = self._backward_pass(y, output)
                self._update_weights(weight_gradients)

            train_accuracy, val_accuracy = self._print_learning_progress(start_time, iteration, x_train, y_train, x_val, y_val)
            history['accuracy'].append(train_accuracy)
            history['val_accuracy'].append(val_accuracy)
        return history