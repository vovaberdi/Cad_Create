
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeCylinder, BRepPrimAPI_MakeTorus
from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Cut
from OCC.Core.BRepFilletAPI import BRepFilletAPI_MakeFillet
from OCC.Core.TopExp import TopExp_Explorer
from OCC.Core.TopAbs import TopAbs_EDGE
from OCC.Core.TopoDS import topods
from OCC.Core.STEPControl import STEPControl_Writer, STEPControl_AsIs
from OCC.Core.IFSelect import IFSelect_RetDone
from OCC.Core.gp import gp_Ax2, gp_Pnt, gp_Dir

# Create the main body of the cup (a solid cylinder)
cup_body = BRepPrimAPI_MakeCylinder(20, 50).Shape()

# Hollow out the cup by creating a slightly smaller cylinder and performing a Boolean cut
inner_cup = BRepPrimAPI_MakeCylinder(18, 48).Shape()  # Slightly smaller for wall thickness
cup_body_hollow = BRepAlgoAPI_Cut(cup_body, inner_cup).Shape()

# Apply a fillet to the top edge of the cup for a smooth finish
fillet = BRepFilletAPI_MakeFillet(cup_body_hollow)

# Explore the edges of the shape and add them to the fillet operation
edge_explorer = TopExp_Explorer(cup_body_hollow, TopAbs_EDGE)
edges_found = False
while edge_explorer.More():
    edge = topods.Edge(edge_explorer.Current())  # Use the correct static method
    try:
        fillet.Add(3.0, edge)  # 3.0 is the radius of the fillet
        edges_found = True
    except Exception as e:
        print(f"Failed to add fillet to edge: {e}")
    edge_explorer.Next()

# Check if any edges were found and filleted
cup_with_fillet = None
if not edges_found:
    print("No valid edges found for filleting.")
else:
    try:
        cup_with_fillet = fillet.Shape()  # This will fail if no fillet can be created
    except Exception as e:
        print(f"Fillet creation failed: {e}")

# Check if the filleting process was successful
if cup_with_fillet is None:
    print("Skipping filleting due to errors.")
    cup_with_fillet = cup_body_hollow  # Use the hollow cup without filleting to proceed

# Adjust the handle position close to the cup
handle_axis = gp_Ax2(gp_Pnt(25, 0, 25), gp_Dir(0, 1, 0), gp_Dir(1, 0, 0))  # Position the handle close to the cup
handle = BRepPrimAPI_MakeTorus(handle_axis, 10, 4).Shape()

# Now we cut the part of the handle that goes inside the inner cup
handle_trimmed = BRepAlgoAPI_Cut(handle, inner_cup).Shape()  # Cut the intersecting part of the handle

# Combine the trimmed handle and the cup body using a Boolean union
from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Fuse
cup_with_handle = BRepAlgoAPI_Fuse(cup_with_fillet, handle_trimmed).Shape()

# Export to STEP file
step_writer = STEPControl_Writer()
step_writer.Transfer(cup_with_handle, STEPControl_AsIs)  # Correctly passing the STEPControl_AsIs flag
status = step_writer.Write("cup_model.step")

if status == IFSelect_RetDone:
    print("Cup STEP file created successfully.")
else:
    print("Failed to create the STEP file.")
