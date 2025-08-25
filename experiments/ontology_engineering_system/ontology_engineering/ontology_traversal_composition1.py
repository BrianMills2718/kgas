from owlready2 import *

# Create an ontology in memory
onto = get_ontology("http://example.org/combined_inference.owl")

with onto:
    class Person(Thing):
        pass

    class Post(Thing):
        pass

    # 1) Define a transitive relationship
    class follows(Person >> Person, TransitiveProperty):
        pass

    # 2) Define a property for "tweets"
    class tweets(Person >> Post):
        pass

    # 3) Define a property for "might_have_seen"
    class might_have_seen(Person >> Post):
        pass

    # 4) Set up our property chain: might_have_seen = follows o tweets
    might_have_seen.equivalent_to.append(PropertyChain([follows, tweets]))

# Create individuals
alice = onto.Person("Alice")
bob = onto.Person("Bob")
charlie = onto.Person("Charlie")
post_x = onto.Post("PostX")

# Assert direct relationships
alice.follows.append(bob)       # (A) Alice follows Bob
bob.follows.append(charlie)     # (B) Bob follows Charlie
charlie.tweets.append(post_x)   # (C) Charlie tweets post_x

# Before inference
print("Before reasoner:")
for p in onto.Person.instances():
    print(f"  Person: {p.name}, follows:", [x.name for x in p.follows])
    print(f"               might_have_seen:", [x.name for x in p.might_have_seen])

# Run reasoner *inside* 'with onto' so inferences are placed INTO 'onto'
with onto:
    sync_reasoner_pellet(infer_property_values=True)

print("\nAfter reasoner:")

# Check the transitive closure of follows
for p in onto.Person.instances():
    print(f"  Person: {p.name}, follows (direct + inferred):", [x.name for x in p.follows])
    print(f"               might_have_seen (direct + inferred):", [x.name for x in p.might_have_seen])

# Also check the Owlready2 "INDIRECT_" usage for transitive property
print("\nCheck INDIRECT usage for 'follows':")
for p in onto.Person.instances():
    print(f"  Person: {p.name}, INDIRECT_follows:", [x.name for x in p.INDIRECT_follows])
