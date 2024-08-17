# MPS Generator testing:

This is a small guide for testing the MPS model translation with generator tests, more details can be found on [this link](https://www.jetbrains.com/help/mps/testing-languages.html#testscreation).

1. Create a new Model in a fitting Solution using by right-click.

![DeMAF_Overview](./pictures/1.png)

2. Enter a proper name and make sure to **select** "@tests"

![DeMAF_Overview](./pictures/2.png)

3. Import the language "jetbrains.mps.lang.test.generator" and finish the test model creation.

![DeMAF_Overview](./pictures/3.png)

4. Now you can start creating generator tests, by right-click on the test model.

![DeMAF_Overview](./pictures/4.png)

5. After creating the generator test you need to create the input model you want to test.

![DeMAF_Overview](./pictures/5.png)

6. Enter a proper name and make sure to **un**select the "@test".

![DeMAF_Overview](./pictures/6.png)

7. Add the language of the input model and finish the model creation. Do the same creation for the expacted output model.

![DeMAF_Overview](./pictures/7.png)

8. Finally you should have these modules:

![DeMAF_Overview](./pictures/8.png)

---
## Creating tests

To create tests you need to create specific input and output models:

1. Right-click on the models and create a new deployment model for each.

![DeMAF_Overview](./pictures/create_model1.png)

2. Now add the features you want to test and define the expected output. Use the keys **ctrl + space** in the deployment models to add components.

![DeMAF_Overview](./pictures/create_model2.png)

3. After adjusting these models, write the test in the generator test file. Use **ctrl + space** to see the possible testing options.

![DeMAF_Overview](./pictures/create_model3.png)

4. Now you can run the test by using **right-click**.


