# Owlready2 Logical Inference Notes

## 1) Defining a Transitive Property
- You can define a transitive property by subclassing from `TransitiveProperty`:
  ```python
  class follows(Person >> Person, TransitiveProperty):
      pass
  ```
- Or by specifying characteristics:
  ```python
  class follows(ObjectProperty):
      characteristics = [TransitiveProperty]
      domain = [Person]
      range = [Person]
  ```
- Then running the reasoner inside `with onto:` will infer any transitive relationships (e.g., X follows Y and Y follows Z implies X follows Z).

## 2) Defining a Property Chain (Composition)
- Use the `PropertyChain` class and append it to the `.equivalent_to` list of your intended property.  
- Example: If we want "might_have_seen" to hold whenever Person A *follows* Person B and Person B *tweets* Post P, we do:
  ```python
  class might_have_seen(Person >> Post):
      pass

  # "might_have_seen = follows o tweets"
  might_have_seen.equivalent_to.append(PropertyChain([follows, tweets]))
  ```
- Ensure that:  
  1. `follows` goes from Person to Person.  
  2. `tweets` goes from Person to Post.  
  3. `might_have_seen` goes from Person to Post.  
  This way, the chain Person → Person → Post is well-defined.

## 3) Running the Reasoner
- Always run the reasoner **inside** a `with onto:` block so that inferred facts appear in the same ontology:
  ```python
  with onto:
      sync_reasoner_pellet(infer_property_values=True)
  ```
- After inference, check both direct property links and also `INDIRECT_` links for transitive closures.

## 4) Troubleshooting
- If you **don't see** inferred facts:
  1. Verify you ran `sync_reasoner_pellet(infer_property_values=True)` *inside* `with onto:`.  
  2. Double-check your domain and range definitions or class-based syntax (`Person >> Post`).  
  3. Confirm you spelled property names, class names, and individuals exactly the same.  
  4. Sometimes saving and reloading the ontology, or using a different reasoner (like HermiT), can resolve issues.  
  5. Check if your version of Pellet supports OWL 2 property chains fully.  
  6. You can also try using `INDIRECT_` attributes for transitive property expansions (e.g., `alice.INDIRECT_follows`).

By following these guidelines, you can *combine* **transitive** properties and **property chains** to yield **compositional** inferences in Owlready2!
